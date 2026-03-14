from src.core import TranscriberAi


PATH_FILE = "file_tests/WhatsApp Ptt 2026-03-09 at 18.26.08.ogg"

meetingai = TranscriberAi(file_input= PATH_FILE)
transcriber = meetingai.execute()


print(transcriber)

