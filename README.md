# 🎙️ MeetMind AI

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-Integration-green)
![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black)
![Faster Whisper](https://img.shields.io/badge/Faster_Whisper-Transcription-orange)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Audio_Processing-red)

## 📌 Overview
**MeetMind AI** is a terminal application developed to act as your personal meeting assistant. The system transcribes audio and video files locally, distills important information (removing idle chatter and noise), and automatically generates a structured **Minutes of Meeting (MoM)** report. All of this operates 100% locally, guaranteeing complete data privacy through the Ollama ecosystem.

## 🚀 System Architecture
The project adopts principles of separation of responsibilities. The main components include:
1. **Media Processing (`app.py` & `src/core.py`):** - Uses `FFmpeg` to extract and standardize audio to 16kHz mono (WAV), optimizing transcription.
2. **Transcription Engine:** - Uses the `large-v3-turbo` model from *Faster Whisper* to ensure fast and accurate transcriptions with VAD (Voice Activity Detection) filtering.
3. **Data Distillation and Semantic Chunking:** - Applies *Semantic Chunking* (`langchain_experimental`) to slice long texts.
   - An LLM agent processes each fragment to retain only facts, dates, and decisions (removing the "noise").
1. **Executive Report Generation (MoM):** - A specialized agent processes the distilled memory and structures a clear report containing the Summary, Decisions Made, and an Action Plan (Actions, Responsible Parties, Deadlines).

## ⚙️ Prerequisites
Before starting, make sure you have:
* Python 3.10 or higher installed.
* [FFmpeg](https://ffmpeg.org/download.html) installed and configured in the operating system's environment variables (`PATH`).
* [Ollama](https://ollama.com/download) is installed and running in your local environment.

You should also pull the local templates in the terminal:
```bash
# Main LLM Template for Generation and Distillation
ollama pull gemma3n:e4b

# Embeddings Template
ollama pull embeddinggemma:300m
```

## 🛠️ Installation and Configuration
1. **Clone the repository:**
```python
git clone https://github.com/RaphelMar/meetmind_ai.git
cd meetmind_ai
```

2. **Create and activate the virtual environment:**
```python
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

3. **Install the dependencies:**
```python
pip install -r requirements.txt
```

4. **Environment Variable Configuration:**
Create a `.env` file in the project root configuring the destination folder for the reports:
```python
OUTPUT_PATH="./temp"
```

## 💻 How to Run

Start the application by running:
```bash
python app.py
```

When prompted by the terminal, **drag and drop the audio or video file** from your meeting and press ENTER. The system will handle the entire workflow (audio extraction, transcription, distillation, and reporting).

## 📂 Directory Structure
```Code Snippet
📦 meetmind_ai
┣ 📂 src
┃ ┣ 📜 core.py # Conversion logic, transcription (Whisper) and LLM pipelines
┃ ┗ 📜 prompts.py # Strict behavior templates for AI Agents
┣ 📂 temp # Folder for temporary audio and generated reports
┣ 📜 .env # Environment variables (not versioned)
┣ 📜 .gitignore # Git ignore settings
┣ 📜 app.py # Application entry point via Terminal
┣ 📜 requirements.txt # Python dependencies
┗ 📜 README.md # Documentation Project
```
## 📝 Technical Decision Record (ADR)
- **Two-Step Distillation:** Instead of sending the entire transcript directly to the AI ​​to generate the minutes, we created a Distiller Agent. This prevents AI hallucinations in very long meetings, ensuring that the final agent only reads the concrete facts.
- **Semantic Chunking:** Adopted to avoid the abrupt cutting of context that usually occurs with traditional methods of splitting text by characters.

## 🗺️ Upcoming Implementations
- [ ] **Web Interface with Streamlit:** Development of a user-friendly UI in Streamlit so that users without technical knowledge can easily use the system (Simplified upload, visual progress, and visualization of the generated minutes on the screen).