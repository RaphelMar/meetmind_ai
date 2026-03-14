from src.core import TranscriberAi


PATH_FILE = "file_tests/JLC Assessoria Empresarial.m4a"

meetingai = TranscriberAi(file_input= PATH_FILE)
transcriber = meetingai.execute()


print(transcriber)

