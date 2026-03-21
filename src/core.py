import os
import subprocess
from tqdm import tqdm
from src.prompts import SystemPrompt
from faster_whisper import WhisperModel
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_experimental.text_splitter import SemanticChunker

class TranscriberAi():
    def __init__(self, file_input: str, output_wave: str = "temp/temp_audio_16k.wav"):
        self.file_input = file_input
        self.output_wav = output_wave

    def _convert_to_wav(self, file_path: str, output_wave: str) -> None:
        """
        Extract audio using ffmpeg, ensuring mono 16kHz PCM.
        The command suppresses stdout and captures stderr; on failure a RuntimeError is raised.
        """
        cmd = [
            "ffmpeg",
            "-i", file_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-y",
            output_wave,
        ]
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {result.stderr.strip()}")

    def _get_transcript(self, audio_path: str) -> str:
        """
        Uses Whisper's large-v3-turbo model to perform transcriptions
        """
        model = WhisperModel(model_size_or_path="large-v3-turbo", device="cpu", compute_type="int8")
        segments, info = model.transcribe(
            audio_path,
            beam_size=8,
            language="pt",
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
            repetition_penalty=1.15,
            condition_on_previous_text=False
        )

        transcribed_texts = []

        # Visual progress bar in terminal
        with tqdm(total=round(info.duration, 2), unit=" seg", desc="Transcribing") as pbar:
            for segment in segments:
                transcribed_texts.append(segment.text)
                pbar.update(segment.end - pbar.n)

        return " ".join(transcribed_texts)

    def _clean_file_temp(self, audio_path: str) -> None:
        os.remove(path=audio_path)

    def _distill_transcript(self, transcript: str, llm, embeddings) -> str:
        """
        Slice the text by semantics and use LLM to extract only facts,
        throwing the noise in the trash.
        """
        # 1. Semantic Chunking
        text_splitter = SemanticChunker(
            embeddings,
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=92
        )
        docs = text_splitter.create_documents([transcript])
        print(f"      Text divided into {len(docs)} semantic chunks.")

        # 2. LLM Distillation
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", SystemPrompt.agent_distiller()),
            ("user", "Trecho da transcrição:\n\n{text}")
        ])
        chain = prompt_template | llm | StrOutputParser()
        
        distilled_facts = []
        for i, doc in enumerate(tqdm(docs, desc="Distilling", unit="chunk")):
            chunk_text = doc.page_content.strip()
            
            # Length-based Pruning
            if len(chunk_text.split()) < 10:
                continue
                
            response = chain.invoke({"text": chunk_text}).strip()
            if "[EMPTY]" not in response.upper() and response != "":
                distilled_facts.append(f"### Fragment {i+1}\n{response}")
        
        return "\n\n".join(distilled_facts)

    def _generate_report(self, transcript: str, llm_instance):
        """
        Now agent receive the Distilled Memory (small and rich) instead of the raw transcript (giant and noisy).
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", SystemPrompt.agent_mom_master()),
            ("user", "Texto da Reunião: {text}")
        ])

        chain = prompt | llm_instance | StrOutputParser()

        return chain.invoke({"text": transcript})
    
    def execute(self):
        """
        Pipeline execution, media conversion, meeting transcription, and report generation.
        """
        # Converts media to WAV format.
        print("[1/4] Extracting and preparing the audio with FFmpeg...")
        self._convert_to_wav(self.file_input, self.output_wav)

        # Generates the transcript
        print("\n[2/4] Starting transcription (VAD activated)...")
        transcript = self._get_transcript(self.output_wav)

        # Delete the temporary WAV file (if it exists).
        if os.path.exists(self.output_wav):
            self._clean_file_temp(self.output_wav)

        # Instantiating models
        llm = ChatOllama(model="gemma3n:e4b", temperature=0.1, num_ctx=8192, num_gpu=999)
        embeddings = OllamaEmbeddings(model="embeddinggemma:300m")

        print("\n[3/4] Distilling the transcription (Extracting facts and removing noise)...")
        distilled_memory = self._distill_transcript(transcript, llm, embeddings)

        # Agents responsible for generating the minutes, executive summary, and action plan.
        print("\n[4/4] Transcription complete! Generating report with gemma3n:e4b")
        print("Attention: Gemma is reading the entire text. This may take a few minutes. Please wait and do not close the terminal...")
        return self._generate_report(distilled_memory, llm)