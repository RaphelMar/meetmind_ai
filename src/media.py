from moviepy import AudioFileClip, VideoFileClip


def convert_to_wav(file_path: str) -> None:
    output_wav = "temp/temp_audio_16k.wav"

    # Upload the video or audio
    clip = AudioFileClip(file_path) if file_path.endswith((".mp3", ".ogg", ".wav", "m4a")) else VideoFileClip(file_path).audio

    # Exports at 16kHz, Mono (Best for Whisper)
    clip.write_audiofile(output_wav, fps= 16000, nbytes=2, codec='pcm_s16le', ffmpeg_params=["-ac", "1"])
