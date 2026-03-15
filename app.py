import os
from src.core import TranscriberAi
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Verify that ffmpeg is available in the system PATH
import shutil, sys
if shutil.which("ffmpeg") is None:
    print("Error: ffmpeg not found. Please install ffmpeg and ensure it is available in your PATH.")
    sys.exit(1)

OUTPUT_PATH = Path(os.getenv("OUTPUT_PATH", ""))

def main():
    print("="*50)
    print("🎙️ WELCOME TO MEETMIND AI (Terminal Mode) 🎙️")
    print("="*50)

    # Asks the user for the file path (they can drag the file to the terminal).
    file_path = input("\nDrag the audio file here and press ENTER:\n> ").strip()

    # Remove quotation marks if the terminal adds them when dragging the file.
    file_path = file_path.strip("'\"")

    if not os.path.exists(file_path):
        print("Error: File not found! Check the path.")
        return

    print("\nStarting the meeting processing...")

    try:
        # Instantiate the class and execute it.
        meeting_ai = TranscriberAi(file_input=file_path)
        markdown_result = meeting_ai.execute()

        # Save the result to a file.
        now = datetime.now()
        formatted_data = now.strftime("%Y-%m-%d-%H%M")
        output_name = OUTPUT_PATH / f"{formatted_data}.md"

        with open(output_name, "w", encoding="utf-8") as f:
            f.write(markdown_result)

        print("\n" + "="*50)
        print(f"SUCCESS! Report saved as: {output_name}")
        print("="*50 + "\n")

    except Exception as e:
        print(f"\nAn error occurred during execution: {e}")

if __name__ == "__main__":
    main()