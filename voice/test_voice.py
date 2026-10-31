import speech_recognition as sr
import subprocess


def speak(text):
    print("Nova:", text)

    powershell_command = f'''
Add-Type -AssemblyName System.Speech
$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
$speaker.Speak("{text}")
'''

    subprocess.run(
        ["powershell", "-NoProfile", "-Command", powershell_command],
        check=True
    )


recognizer = sr.Recognizer()


speak("Hello Chris. I am Nova. How can I help you?")


while True:

    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        text = text.lower().strip()

        print("You:", text)

        # Stop commands
        stop_words = [
            "goodbye",
            "bye",
            "bye bye",
            "exit",
            "quit",
            "stop",
            "close nova"
        ]

        if any(command in text for command in stop_words):
            speak("Goodbye Chris.")
            break

        # Basic responses
        if "your name" in text:
            speak("My name is Nova.")

        elif "my name" in text:
            speak("Your name is Chris.")

        elif "how are you" in text:
            speak("I'm doing great, Chris. Thanks for asking.")

        elif "hello" in text or "hi" in text:
            speak("Hello Chris. How can I help you?")

        else:
            speak(
                f"I heard you say {text}, "
                "but I don't know how to respond to that yet."
            )

    except sr.UnknownValueError:
        print("I didn't understand that.")

    except sr.RequestError:
        print("Could not connect to the speech recognition service.")
