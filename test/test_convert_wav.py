import subprocess

INPUT_FILE = "/Users/raphaelresende/Downloads/JLC Assessoria Empresarial.m4a"
OUTPUT_FILE = "temp/temp_audio_16k.wav"


def convert_to_wav(file_path: str, output_wave: str) -> None:
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

if __name__ == "__main__":
    convert_to_wav(file_path= INPUT_FILE, output_wave= OUTPUT_FILE )