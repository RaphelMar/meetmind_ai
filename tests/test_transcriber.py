from src.transcriber import get_transcript

import time
from datetime import timedelta

start = time.time()


AUDIO_PATH = "temp/temp_audio_16k.wav"


print(get_transcript(audio_path= AUDIO_PATH))


end = time.time()
total_time = timedelta(seconds=int(end - start))

print(f"Tempo de execução: {total_time}")