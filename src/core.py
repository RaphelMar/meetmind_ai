import os
import subprocess
from tqdm import tqdm
from src.prompts import SystemPrompt
from faster_whisper import WhisperModel
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

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
            beam_size=6,
            language="pt",
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
            repetition_penalty=1.15,
            condition_on_previous_text=False
        )

        transcribed_texts = []

        # Visual progress bar in terminal
        with tqdm(total=round(info.duration, 2), unit=" seg", desc="Transcrevendo") as pbar:
            for segment in segments:
                transcribed_texts.append(segment.text)
                pbar.update(segment.end - pbar.n)

        return " ".join(transcribed_texts)

    def _clean_file_temp(self, audio_path: str) -> None:
        os.remove(path=audio_path)

    def _run_agent(self, transcript: str, role_prompt: str, llm_instance):
        """
        Run a single LangChain agent
        Parameters
        ----------
        transcript: str
            The meeting transcript.
        role_prompt: str
            System prompt for the specific agent.
        llm_instance: ChatOllama
            Pre‑instantiated LLM client (singleton).
        """
        # System prompt and chain creation – keep exact pattern
        prompt = ChatPromptTemplate.from_messages([
            ("system", role_prompt),
            ("user", "Texto da Reunião: {text}")
        ])

        chain = prompt | llm_instance | StrOutputParser()

        return chain.invoke({"text": transcript})
    
    def _generate_reports(self, transcript: str):
        """
        Generate executive summary, minutes, and action plan concurrently.
        Returns a tuple (executive_summary, meeting_minutes, action_plan).
        """
        # Instantiate the LLM once (singleton for this run)
        llm = ChatOllama(model="gemma3n:e4b", temperature=0.1, num_ctx=32768, num_gpu=999)

        # Preparing the documents: Executive Summary, Minutes, and Action Plan
        executive_summary = self._run_agent(transcript, SystemPrompt.agent_executive_summary(), llm)
        meeting_minutes = self._run_agent(transcript, SystemPrompt.agent_ata(), llm)
        action_plan = self._run_agent(transcript, SystemPrompt.agent_action_plan(), llm)

        return executive_summary, meeting_minutes, action_plan

    def execute(self):
        """
        Pipeline execution, media conversion, meeting transcription, and report generation.
        """
        # Converts media to WAV format.
        print("[1/3] Extracting and preparing the audio with FFmpeg...")
        self._convert_to_wav(self.file_input, self.output_wav)

        # Generates the transcript
        print("[2/3] Starting transcription (VAD activated)...")
        transcript = self._get_transcript(self.output_wav)

        # Delete the temporary WAV file (if it exists).
        if os.path.exists(self.output_wav):
            self._clean_file_temp(self.output_wav)

        # Agents responsible for generating the minutes, executive summary, and action plan.
        print("\n[3/3] Transcription complete! Generating report with gemma3n:e4b")
        print("Attention: Gemma is reading the entire text. This may take a few minutes. Please wait and do not close the terminal...")
        executive_summary, meeting_minutes, action_plan = self._generate_reports(transcript)

        return f"""
        # Relatório de Reunião MeetMind AI
        ## Sumário Executivo
        {executive_summary}

        ---

        ## Ata Detalhada
        {meeting_minutes}

        ---

        ## Plano de Ação e Tarefas
        {action_plan}
        """