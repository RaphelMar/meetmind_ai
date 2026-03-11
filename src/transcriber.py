from faster_whisper import WhisperModel




def get_transcript(audio_path: str):

    model = WhisperModel(model_size_or_path= "large-v3-turbo", device= "cpu", compute_type= "int8")
    segments, _ = model.transcribe(audio_path, beam_size= 8, language= "pt")

    return " ".join([s.text for s in segments])


