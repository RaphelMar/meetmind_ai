import os
from faster_whisper import WhisperModel
from langchain_ollama import ChatOllama
from moviepy import AudioFileClip, VideoFileClip
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.prompts import SystemPrompt
from tqdm import tqdm

class TranscriberAi():
    def __init__(self, file_input: str, output_wave: str = "temp/temp_audio_16k.wav"):
        self.file_input = file_input
        self.output_wav = output_wave

    def _convert_to_wav(self, file_path: str, output_wave: str) -> None:
        # Extrai o áudio do vídeo ou processa o áudio existente
        clip = AudioFileClip(file_path) if file_path.endswith((".mp3", ".ogg", ".wav", ".m4a")) else VideoFileClip(file_path).audio
        # logger=None oculta a saída suja do moviepy na consola
        clip.write_audiofile(output_wave, fps=16000, nbytes=2, codec='pcm_s16le', ffmpeg_params=["-ac", "1"], logger=None)

    def _get_transcript(self, audio_path: str) -> str:
        model = WhisperModel(model_size_or_path="large-v3-turbo", device="cpu", compute_type="int8")

        # ==========================================
        # PARÂMETROS ANTI-ALUCINAÇÃO E VAD APLICADOS
        # ==========================================
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

        # Barra de progresso visual no terminal
        with tqdm(total=round(info.duration, 2), unit=" seg", desc="Transcrevendo") as pbar:
            for segment in segments:
                transcribed_texts.append(segment.text)
                # Atualiza a barra com o tempo processado
                pbar.update(segment.end - pbar.n)

        return " ".join(transcribed_texts)

    def _clean_file_temp(self, audio_path: str) -> None:
        os.remove(path=audio_path)

    def _run_agent(self, transcript: str, role_prompt: str):
        llm = ChatOllama(model="llama3.2:3b", temperature=0.1, num_ctx=32768, num_gpu= 999)

        # System prompt e chain de execução
        prompt = ChatPromptTemplate.from_messages([
            ("system", role_prompt),
            ("user", "Texto da Reunião: {text}")
        ])
        chain = prompt | llm | StrOutputParser()

        return chain.invoke({"text": transcript})
    
    def execute(self):
        # Converte a média para formato WAV.
        print("[1/4] A extrair e preparar o áudio com MoviePy...")
        self._convert_to_wav(self.file_input, self.output_wav)

        # Gera a transcrição
        print("[2/4] A iniciar a transcrição (VAD ativado)...")
        transcript = self._get_transcript(self.output_wav)

        # Apaga o ficheiro WAV temporário
        self._clean_file_temp(self.output_wav)

        # Agentes a gerar as atas, sumário executivo e plano de ação.
        print("[4/4] Transcrição concluída! A gerar relatório com Llama 3.2:8b")
        print("Atenção: O Ollama está a ler o texto completo. Isto pode demorar alguns minutos. Por favor, aguarde e não feche o terminal...")
        executive_summary = self._run_agent(transcript=transcript, role_prompt=SystemPrompt.agent_executive_summary())
        meeting_minutes = self._run_agent(transcript=transcript, role_prompt=SystemPrompt.agent_ata())
        action_plan = self._run_agent(transcript=transcript, role_prompt=SystemPrompt.agent_action_plan())

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