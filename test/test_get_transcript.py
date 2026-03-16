from faster_whisper import WhisperModel
from tqdm import tqdm

FILE_INPUT = "temp/temp_audio_16k.wav"

def get_transcript(audio_path: str) -> str:
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


if __name__ == "__main__":
     
    transcriber = get_transcript(FILE_INPUT)

    with open("temp/teste.txt", "w", encoding="utf-8") as file:
        file.write(transcriber)