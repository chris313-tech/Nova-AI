Nova AI – Personal Desktop Voice Assistant

Nova AI is a Python-based personal desktop voice assistant developed for Windows. It combines voice interaction, artificial intelligence, persistent memory and desktop automation to create a more natural way of interacting with a computer.

The project is being developed as an exploration of Python programming, artificial intelligence, speech technologies and Windows automation.

Features

- **Voice Recognition:** Uses Vosk for offline speech recognition.
- **Text-to-Speech:** Generates spoken responses using Windows speech capabilities.
- **AI Integration:** Connects to Ollama and the Qwen2.5:3B language model for AI-powered responses.
- **Persistent Memory:** Uses JSON files to store and retrieve information.
- **Conversational Intelligence:** Recognises greetings, questions and everyday conversational commands.
- **Desktop Automation:** Supports opening applications, navigating folders and executing computer commands.
- **Graphical Interface:** Includes a custom interface for assistant interaction.

Technologies Used

- Python
- Vosk
- SpeechRecognition
- PyAudio
- pyttsx3
- Ollama
- Qwen2.5:3B
- JSON
- Windows PowerShell

Project Structure

```text
Nova-AI/
│
├── core/
│   ├── __init__.py
│   ├── aichat.py
│   ├── brain.py
│   ├── command.py
│   ├── memory.py
│   └── novaui.py
│
├── voice/
│   ├── __init__.py
│   ├── test_speech.py
│   └── test_voice.py
│
├── data/
├── main.py
├── requirements.txt
├── .gitignore
├── StartNova.bat
└── StartNova.vbs
```

Download and Installation

1. Download Nova AI

- Open this repository: https://github.com/chris313-tech/Nova-AI
- Click the green **Code** button.
- Select **Download ZIP**.
- Extract the downloaded ZIP file.

2. Install Python

Install Python 3.13 or a compatible version for the project's dependencies.

3. Install Dependencies

Open Command Prompt inside the extracted Nova-AI folder and run:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

4. Install Ollama

Download and install Ollama:

https://ollama.com/

Download the required language model:

```bash
ollama pull qwen2.5:3b
```

Ensure Ollama is running before starting Nova.

5. Set Up Vosk

Download a compatible Vosk English speech recognition model:

https://alphacephei.com/vosk/models

Extract the model into the main Nova-AI directory and name its folder:

```text
vosk-model/
```

The folder should be alongside `main.py`.

6. Run Nova AI

Start Nova using:

```bash
python main.py
```

Alternatively, use the supplied Windows launcher if configured.

Project Goal

Nova AI is an ongoing personal project focused on developing a locally operated desktop assistant capable of understanding voice commands, responding intelligently, remembering useful information and performing everyday computer tasks.

The long-term vision is to build a more capable personal AI assistant with improved natural-language understanding, automation and offline functionality.

Developer

**Chris**

GitHub: https://github.com/chris313-tech

**Project:** Nova AI  
**Status:** Ongoing Development
