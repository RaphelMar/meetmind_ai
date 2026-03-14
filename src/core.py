import os
from faster_whisper import WhisperModel
from langchain_ollama import ChatOllama
from moviepy import AudioFileClip, VideoFileClip
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tqdm import tqdm


from src.prompts import SystemPrompt


class TranscriberAi():
    def __init__(self, file_input: str, output_wave: str = "temp/temp_audio_16k.wav"):
        self.file_input = file_input
        self.output_wav = output_wave

    def _convert_to_wav(self, file_path: str, output_wave: str) -> None:
        # Upload the video or audio
        clip = AudioFileClip(file_path) if file_path.endswith((".mp3", ".ogg", ".wav", "m4a")) else VideoFileClip(file_path).audio
        clip.write_audiofile(output_wave, fps= 16000, nbytes=2, codec='pcm_s16le', ffmpeg_params=["-ac", "1"])

    def _get_transcript(self, audio_path: str) -> str:
        # The large-v3-turbo model is best for long and technical meetings.
        print("teste")
        model = WhisperModel(model_size_or_path= "large-v3-turbo", device= "cpu", compute_type= "int8")

        segments, info = model.transcribe(audio_path, beam_size= 8, language= "pt")

        print(segments)

        transcribed_texts = []

        # Creates a progress bar based on the audio duration in seconds.
        with tqdm(total=round(info.duration, 2), unit=" seg", desc="Transcrevendo áudio") as pbar:
            for segment in segments:
                transcribed_texts.append(segment.text)
                
                # For each processed segment, we update the bar to the end time of the current segment.
                # Since pbar.update() adds to the current value, we only pass the difference (the delta).
                pbar.update(segment.end - pbar.n)

        return " ".join(transcribed_texts)

    def _clean_file_temp(self, audio_path: str) -> None:
        os.remove(path= audio_path)

    def _run_agent(self, transcript: str, role_prompt: str):
        # Defining the model with a low temperature for greater accuracy.
        llm = ChatOllama(model= "llama3.2:3b", temperature= 0.1)

        # System prompt and execution chain
        prompt = ChatPromptTemplate.from_messages([
            ("system", role_prompt),
            ("user", "Texto da Reunião: {text}")
        ])
        chain = prompt | llm | StrOutputParser()

        return chain.invoke({"text": transcript})
    
    def execute(self):
        # Converts media to WAV format.
        self._convert_to_wav(self.file_input, self.output_wav)

        # Generates the transcript
        transcript = self._get_transcript(self.output_wav)

        # Delete temporary WAV file
        self._clean_file_temp(self.output_wav)

        # Agents generating the meeting minutes, executive summary and action plan.
        executive_summary = self._run_agent(transcript= transcript, role_prompt= SystemPrompt.agent_executive_summary())
        meeting_minutes = self._run_agent(transcript= transcript, role_prompt= SystemPrompt.agent_ata())
        action_plan = self._run_agent(transcript= transcript, role_prompt= SystemPrompt.agent_action_plan())

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

        


    