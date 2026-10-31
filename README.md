 Nova AI – Personal Desktop Voice Assistant

Nova AI is a Python-based personal desktop voice assistant developed for Windows. It is designed to help users interact with their computers through voice commands, perform everyday tasks, and receive AI-powered responses.

The project combines speech recognition, text-to-speech, local AI integration, persistent memory, and Windows automation.

Features

- **Voice Interaction:** Supports voice-based interaction.
- **Speech Recognition:** Uses Vosk for offline speech recognition.
- **Text-to-Speech:** Uses Windows speech capabilities to generate spoken responses.
- **AI Integration:** Connects to a locally running Ollama instance using the Qwen2.5:3B model.
- **Persistent Memory:** Stores and retrieves information using JSON-based memory.
- **Conversational Intelligence:** Handles greetings, questions, acknowledgements, and basic conversations.
- **Windows Automation:** Designed to execute desktop commands and open Windows applications.
- **Custom Assistant:** Personalised assistant identity and responses.

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
│   ├── aichat.py
│   ├── brain.py
│   ├── command.py
│   ├── memory.py
│   └── novaui.py
│
├── voice/
│   ├── test_speech.py
│   └── test_voice.py
│
├── data/
│
├── main.py
├── requirements.txt
├── .gitignore
├── startNova.bat
└── StartNova.vbs
```

Setup

1. Clone this repository.
2. Install Python and create a virtual environment.
3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Install [Ollama](https://ollama.com/) and download the model:

```bash
ollama pull qwen2.5:3b
```

5. Ensure Ollama is running.
6. Connect a microphone and run:

```bash
python main.py
```
Project Goal

Nova AI is an ongoing personal project focused on exploring artificial intelligence, Python development, voice interaction, and desktop automation.

The long-term goal is to develop a more capable personal assistant that can understand natural language, manage computer tasks, remember useful information, and operate locally wherever possible.

**Developer:** Chris  
**Project:** Nova AI
