import json
from vosk import Model, KaldiRecognizer
import speech_recognition as sr
import subprocess
import os
import re
import shutil
import time
import queue
import threading

from core.brain import NovaBrain
from core.memory import NovaMemory
from core.ai_chat import ask_ai
from core.nova_ui import NovaUI


# =========================================================
# NOVA BRAIN AND MEMORY
# =========================================================

brain = NovaBrain()
memory = NovaMemory()


# =========================================================
# NOVA COMMANDS
# =========================================================

from core.commands import (
    open_calculator,
    open_notepad,
    open_chrome,
    open_settings,
    open_file_explorer,
    open_task_manager,
    open_command_prompt,
    open_control_panel,
    open_vscode,
    open_downloads,
    open_documents,
    open_desktop,
    open_pictures,
    open_music,
    open_videos,
    lock_computer,
    shutdown_computer,
    restart_computer,
    cancel_shutdown,
    create_folder,
    open_file,
    open_folder
)


# =========================================================
# NOVA SPEECH
# =========================================================


def speak(text):
    print("Nova:", text)

    if "ui" in globals():
        ui.add_message("Nova", str(text))
        ui.set_state("speaking")

    try:
        safe_text = str(text).replace("'", "''")

        powershell_command = (
            "Add-Type -AssemblyName System.Speech\n"
            "$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer\n"
            "$speaker.Rate = 1\n"
            f"$speaker.Speak('{safe_text}')\n"
        )

        subprocess.run(
            ["powershell", "-NoProfile", "-Command", powershell_command],
            check=True
        )
    finally:
        if "ui" in globals():
            ui.set_state("idle")
           
# =========================================================
# SPEECH RECOGNITION
# =========================================================

recognizer = sr.Recognizer()

VOSK_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "vosk-model"
)

vosk_model = Model(VOSK_MODEL_PATH)


# =========================================================
# NOVA CURRENT LOCATION
# =========================================================

current_location = os.path.join(
    os.path.expanduser("~"),
    "Desktop"
)


# =========================================================
# LISTEN
# =========================================================




def listen():
    if "ui" in globals():
        ui.set_state("listening")

    try:
        with sr.Microphone() as source:
            print("Adjusting for background noise...")
            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.8
            )

            print("Listening...")

            try:
                audio = recognizer.listen(
                    source,
                    timeout=4,
                    phrase_time_limit=10
                )
            except sr.WaitTimeoutError:
                return ""

        try:
            audio_data = audio.get_raw_data(
                convert_rate=16000,
                convert_width=2
            )

            vosk_recognizer = KaldiRecognizer(
                vosk_model,
                16000
            )

            vosk_recognizer.AcceptWaveform(audio_data)

            result = json.loads(
                vosk_recognizer.FinalResult()
            )

            text = result.get("text", "").strip()

            if not text:
                print("I didn't understand that.")
                return ""

            print("You:", text)
            return text.lower()

        except Exception as error:
            print("Offline speech recognition error:", error)
            return ""

    except Exception as error:
        print("Microphone error:", error)
        return ""

    finally:
        if "ui" in globals():
            ui.set_state("idle")

# =========================================================
# LOCATION HELPER
# =========================================================

def get_special_location(location_name):

    home = os.path.expanduser("~")

    location_name = location_name.lower().strip()

    if location_name in ["document", "documents"]:
        return os.path.join(home, "Documents")

    elif location_name in ["download", "downloads"]:
        return os.path.join(home, "Downloads")

    elif location_name == "desktop":
        return os.path.join(home, "Desktop")

    elif location_name in ["picture", "pictures"]:
        return os.path.join(home, "Pictures")

    elif location_name == "music":
        return os.path.join(home, "Music")

    elif location_name in ["video", "videos"]:
        return os.path.join(home, "Videos")

    return None


# =========================================================
# MEMORY HELPERS
# =========================================================

def remember_information(text):

    content = re.sub(
        r"^remember\s+(that\s+|this\s+)?",
        "",
        text,
        count=1
    ).strip()

    match = re.match(
        r"(.+?)\s+(?:is|are|=)\s+(.+)",
        content
    )

    if not match:
        return False

    key = match.group(1).strip()
    value = match.group(2).strip()

    key = re.sub(
        r"^(my|the)\s+",
        "",
        key
    ).strip()

    key = key.replace(" ", "_")

    memory.remember(key, value)

    speak(
        f"I'll remember that your {match.group(1).strip()} is {value}, Chris."
    )

    return True


def recall_information(text):

    # Favorite language
    if (
        "favorite language" in text
        or "favourite language" in text
    ):

        key = "favorite_language"

        value = memory.recall(key)

        if value:
            speak(
                f"Your favorite language is {value}, Chris."
            )
        else:
            speak(
                "I don't have your favorite language stored yet, Chris."
            )

        return True

    # Generic: "what is my X"
    match = re.search(
        r"what\s+is\s+my\s+(.+)",
        text
    )

    if match:

        key = match.group(1).strip()

        key = re.sub(
            r"^(the|favorite|favourite)\s+",
            "",
            key
        ).strip()

        if "favorite language" in text:
            key = "favorite_language"

        else:
            key = key.replace(" ", "_")

        value = memory.recall(key)

        if value:

            speak(
                f"Your {match.group(1).strip()} is {value}, Chris."
            )

        else:

            speak(
                f"I don't have your {match.group(1).strip()} stored yet, Chris."
            )

        return True

    # "Do you remember..."
    match = re.search(
        r"do you remember my\s+(.+)",
        text
    )

    if match:

        key = match.group(1).strip()

        if "favorite language" in key:
            key = "favorite_language"
        else:
            key = key.replace(" ", "_")

        value = memory.recall(key)

        if value:

            speak(
                f"Yes, Chris. Your {match.group(1).strip()} is {value}."
            )

        else:

            speak(
                f"I don't have that stored, Chris."
            )

        return True

    return False


def forget_information(text):

    content = re.sub(
        r"^forget\s+(that\s+|this\s+)?",
        "",
        text,
        count=1
    ).strip()

    content = re.sub(
        r"^my\s+",
        "",
        content
    ).strip()

    if (
        "favorite language" in content
        or "favourite language" in content
    ):

        key = "favorite_language"

    else:

        key = content.replace(" ", "_")

    result = memory.forget(key)

    speak(result)

    return True


# =========================================================
# START NOVA
# =========================================================

ui = NovaUI()
time.sleep(0.5)


def voice_input_worker():
    """Listen only after the user presses Nova's microphone button."""
    while not ui.stop_event.is_set():
        if not ui.voice_requested.wait(timeout=0.2):
            continue

        ui.voice_requested.clear()
        if ui.stop_event.is_set():
            break

        spoken_text = listen()
        if spoken_text:
            ui.add_message("You", spoken_text)
            ui.input_queue.put(spoken_text)
        else:
            ui.set_status("I didn't catch that. Try the microphone again.")


threading.Thread(target=voice_input_worker, daemon=True).start()
speak("Hello Chris. I am Nova. How can I help you?")

# =========================================================
# MAIN LOOP
# =========================================================


while True:
    if ui.stop_event.is_set():
        break

    # Both typed messages and microphone transcripts arrive here.
    try:
        text = ui.input_queue.get(timeout=0.2)
    except queue.Empty:
        continue

    if ui.stop_event.is_set():
        break

    text = str(text).strip().lower()
    if not text:
        continue

    print("You:", text)

    # =====================================================
    # EXIT NOVA
    # =====================================================

    
    if any(command in text for command in [
        "goodbye",
        "bye",
        "bye bye",
        "exit",
        "quit",
        "stop",
        "close nova"
    ]):

        speak("Goodbye Chris.")

        ui.shutdown()

        break



    # =====================================================
    # REMEMBER INFORMATION
    # =====================================================

    elif (
        text.startswith("remember ")
        or text.startswith("remember that ")
        or text.startswith("remember this ")
    ):

        if not remember_information(text):

            speak(
                "Tell me what you want me to remember, Chris."
            )


    # =====================================================
    # RECALL INFORMATION
    # =====================================================

    elif (
        text.startswith("what is my ")
        or text.startswith("what's my ")
        or text.startswith("do you remember my ")
        or text.startswith("what do you remember")
        or text.startswith("what did i tell you")
    ):

        if not recall_information(text):

            response = brain.think(text)

            speak(response)


    # =====================================================
    # FORGET INFORMATION
    # =====================================================

    elif (
        text.startswith("forget ")
        or text.startswith("forget that ")
        or text.startswith("forget this ")
    ):

        forget_information(text)


    # =====================================================
    # BASIC CONVERSATION
    # =====================================================

    elif (
        "your name" in text
        or "who are you" in text
        or "what are you called" in text
    ):

        response = brain.think(text)

        speak(response)


    elif "my name" in text:

        response = brain.think(text)

        speak(response)


    elif "how are you" in text:

        response = brain.think(text)

        speak(response)


    elif "hello" in text or "hi" in text or "hey" in text:

        response = brain.think(text)

        speak(response)


    # =====================================================
    # FRIENDLY CONVERSATION
    # =====================================================

    elif text in [
        "thank you",
        "thanks",
        "thank you nova",
        "thanks nova"
    ]:

        response = brain.think(text)

        speak(response)


    elif text in [
        "good job",
        "nice",
        "that's nice",
        "awesome",
        "that's awesome",
        "great",
        "that's great"
    ]:

        speak(
            "Thank you, Chris. I appreciate that."
        )


    elif text in [
        "okay",
        "ok",
        "alright",
        "cool"
    ]:

        speak(
            "Alright, Chris."
        )


    # =====================================================
    # CALCULATOR
    # =====================================================

    elif (
        "open calculator" in text
        or "launch calculator" in text
        or "start calculator" in text
        or "run calculator" in text
    ):

        response = open_calculator()

        speak(response)


    # =====================================================
    # NOTEPAD
    # =====================================================

    elif (
        "open notepad" in text
        or "launch notepad" in text
        or "start notepad" in text
        or "run notepad" in text
    ):

        response = open_notepad()

        speak(response)


    # =====================================================
    # CHROME
    # =====================================================

    elif (
        "open chrome" in text
        or "launch chrome" in text
        or "start chrome" in text
        or "run chrome" in text
        or "open google chrome" in text
        or "launch google chrome" in text
        or "start google chrome" in text
    ):

        response = open_chrome()

        speak(response)


    # =====================================================
    # SETTINGS
    # =====================================================

    elif (
        "open settings" in text
        or "open windows settings" in text
        or "launch settings" in text
        or "launch windows settings" in text
        or "start settings" in text
        or "start windows settings" in text
        or "open pc settings" in text
        or "open computer settings" in text
    ):

        response = open_settings()

        speak(response)


    # =====================================================
    # FILE EXPLORER
    # =====================================================

    elif (
        "open file explorer" in text
        or "launch file explorer" in text
        or "start file explorer" in text
        or "run file explorer" in text
        or "open explorer" in text
        or "launch explorer" in text
        or "start explorer" in text
    ):

        response = open_file_explorer()

        speak(response)


    # =====================================================
    # TASK MANAGER
    # =====================================================

    elif (
        "open task manager" in text
        or "launch task manager" in text
        or "start task manager" in text
        or "run task manager" in text
        or "open taskmgr" in text
        or "launch taskmgr" in text
    ):

        response = open_task_manager()

        speak(response)


    # =====================================================
    # COMMAND PROMPT
    # =====================================================

    elif (
        "open command prompt" in text
        or "launch command prompt" in text
        or "start command prompt" in text
        or "run command prompt" in text
        or "open cmd" in text
        or "launch cmd" in text
        or "start cmd" in text
        or "run cmd" in text
    ):

        response = open_command_prompt()

        speak(response)


    # =====================================================
    # CONTROL PANEL
    # =====================================================

    elif (
        "open control panel" in text
        or "launch control panel" in text
        or "start control panel" in text
        or "run control panel" in text
    ):

        response = open_control_panel()

        speak(response)


    # =====================================================
    # VS CODE
    # =====================================================

    elif (
        "open vs code" in text
        or "launch vs code" in text
        or "start vs code" in text
        or "run vs code" in text
        or "open visual studio code" in text
        or "launch visual studio code" in text
        or "start visual studio code" in text
    ):

        response = open_vscode()

        speak(response)


    # =====================================================
    # DOWNLOADS
    # =====================================================

    elif (
        "open downloads" in text
        or "launch downloads" in text
        or "start downloads" in text
        or "open my downloads" in text
        or "show downloads" in text
    ):

        current_location = os.path.join(
            os.path.expanduser("~"),
            "Downloads"
        )

        response = open_downloads()

        speak(
            response + " This is now my current location."
        )


    # =====================================================
    # DOCUMENTS
    # =====================================================

    elif (
        "open documents" in text
        or "launch documents" in text
        or "start documents" in text
        or "open my documents" in text
        or "show documents" in text
        or "open document folder" in text
    ):

        current_location = os.path.join(
            os.path.expanduser("~"),
            "Documents"
        )

        response = open_documents()

        speak(
            response + " This is now my current location."
        )


    # =====================================================
    # DESKTOP
    # =====================================================

    elif (
        "open desktop" in text
        or "launch desktop" in text
        or "start desktop" in text
        or "open my desktop" in text
        or "show desktop" in text
    ):

        current_location = os.path.join(
            os.path.expanduser("~"),
            "Desktop"
        )

        response = open_desktop()

        speak(
            response + " This is now my current location."
        )


    # =====================================================
    # PICTURES
    # =====================================================

    elif (
        "open pictures" in text
        or "launch pictures" in text
        or "start pictures" in text
        or "open my pictures" in text
        or "show pictures" in text
        or "open picture folder" in text
    ):

        current_location = os.path.join(
            os.path.expanduser("~"),
            "Pictures"
        )

        response = open_pictures()

        speak(
            response + " This is now my current location."
        )


    # =====================================================
    # MUSIC
    # =====================================================

    elif (
        "open music" in text
        or "launch music" in text
        or "start music" in text
        or "open my music" in text
        or "show music" in text
        or "open music folder" in text
    ):

        current_location = os.path.join(
            os.path.expanduser("~"),
            "Music"
        )

        response = open_music()

        speak(
            response + " This is now my current location."
        )


    # =====================================================
    # VIDEOS
    # =====================================================

    elif (
        "open videos" in text
        or "launch videos" in text
        or "start videos" in text
        or "open my videos" in text
        or "show videos" in text
        or "open video folder" in text
    ):

        current_location = os.path.join(
            os.path.expanduser("~"),
            "Videos"
        )

        response = open_videos()

        speak(
            response + " This is now my current location."
        )


    # =====================================================
    # OPEN FOLDER
    # =====================================================

    elif (
        "open the folder" in text
        or "open folder" in text
    ):

        folder_name = re.sub(
            r"^open\s+(?:the\s+)?folder\s+",
            "",
            text
        ).strip()

        folder_path = os.path.join(
            current_location,
            folder_name
        )

        if os.path.isdir(folder_path):

            subprocess.Popen(
                ["explorer.exe", folder_path]
            )

            current_location = folder_path

            speak(
                f"I opened {folder_name}, Chris. "
                "This is now the current location."
            )

        else:

            speak(
                f"I couldn't find the folder {folder_name}, Chris."
            )


    # =====================================================
    # OPEN FILE
    # =====================================================

    elif (
        "open the file" in text
        or "open file" in text
    ):

        file_name = text

        phrases = [
            "open the file",
            "open file"
        ]

        for phrase in phrases:

            if phrase in file_name:

                file_name = file_name.replace(
                    phrase,
                    "",
                    1
                ).strip()

                break

        if file_name:

            file_path = os.path.join(
                current_location,
                file_name
            )

            if os.path.isfile(file_path):

                try:

                    os.startfile(file_path)

                    speak(
                        f"I opened {file_name}, Chris."
                    )

                except Exception:

                    response = open_file(file_name)

                    speak(response)

            else:

                response = open_file(file_name)

                speak(response)

        else:

            speak(
                "Tell me the name of the file you want to open, Chris."
            )


    # =====================================================
    # CREATE FOLDER
    # =====================================================

    elif (
        "create a folder" in text
        or "create a new folder" in text
        or "make a folder" in text
        or "make me a folder" in text
    ):

        folder_name = re.sub(
            r"^(create a new folder|create a folder|make me a folder|make a folder)",
            "",
            text
        ).strip()

        folder_name = re.sub(
            r"^(called|named)\s+",
            "",
            folder_name
        ).strip()

        location = current_location

        location_match = re.search(
            r"\s+(?:in|on)\s+(?:my\s+|the\s+)?"
            r"(documents?|downloads?|desktop|pictures?|music|videos?)"
            r"\s*$",
            folder_name
        )

        if location_match:

            location_name = location_match.group(1)

            explicit_location = get_special_location(
                location_name
            )

            if explicit_location:

                location = explicit_location

                folder_name = folder_name[
                    :location_match.start()
                ].strip()

        folder_name = folder_name.strip(
            " .,?!"
        )

        if folder_name:

            response = create_folder(
                folder_name,
                location
            )

            speak(response)

        else:

            speak(
                "I need a name for the folder, Chris."
            )


    # =====================================================
    # RENAME FOLDER
    # =====================================================

    elif "rename" in text:

        match = re.search(
            r"rename\s+(?:the\s+folder\s+)?(.+?)\s+to\s+(.+)",
            text
        )

        if match:

            old_name = match.group(1).strip()
            new_name = match.group(2).strip()

            location = current_location

            location_match = re.search(
                r"\s+(?:in|on)\s+(?:my\s+|the\s+)?"
                r"(documents?|downloads?|desktop|pictures?|music|videos?)"
                r"\s*$",
                new_name
            )

            if location_match:

                location_name = location_match.group(1)

                explicit_location = get_special_location(
                    location_name
                )

                if explicit_location:

                    location = explicit_location

                    new_name = new_name[
                        :location_match.start()
                    ].strip()

            old_path = os.path.join(
                location,
                old_name
            )

            new_path = os.path.join(
                location,
                new_name
            )

            if not os.path.isdir(old_path):

                speak(
                    f"I couldn't find the folder {old_name} "
                    "in the current location, Chris."
                )

            elif os.path.exists(new_path):

                speak(
                    f"A folder named {new_name} already exists, Chris."
                )

            else:

                try:

                    os.rename(
                        old_path,
                        new_path
                    )

                    speak(
                        f"I renamed {old_name} to {new_name}, Chris."
                    )

                except Exception:

                    speak(
                        "I couldn't rename that folder, Chris."
                    )

        else:

            speak(
                "Tell me the old folder name and the new folder name, Chris."
            )


    # =====================================================
    # DELETE FOLDER
    # =====================================================

    elif (
        text.startswith("delete ")
        or text.startswith("remove ")
    ):

        folder_name = text

        folder_name = re.sub(
            r"^(delete|remove)\s+",
            "",
            folder_name
        ).strip()

        folder_name = re.sub(
            r"^(the\s+)?(folder\s+)",
            "",
            folder_name
        ).strip()

        folder_name = re.sub(
            r"\s+folder$",
            "",
            folder_name
        ).strip()

        location = current_location

        location_match = re.search(
            r"\s+(?:in|on)\s+(?:my\s+|the\s+)?"
            r"(documents?|downloads?|desktop|pictures?|music|videos?)"
            r"\s*$",
            folder_name
        )

        if location_match:

            location_name = location_match.group(1)

            explicit_location = get_special_location(
                location_name
            )

            if explicit_location:

                location = explicit_location

                folder_name = folder_name[
                    :location_match.start()
                ].strip()

        folder_name = folder_name.strip(
            " .,?!"
        )

        folder_path = os.path.join(
            location,
            folder_name
        )

        print("Delete target:", folder_path)

        if os.path.isdir(folder_path):

            speak(
                f"I found the folder {folder_name}. "
                "Do you want me to delete it? "
                "Please say yes or no."
            )

            confirmation = listen()

            print(
                "Delete confirmation:",
                confirmation
            )

            if confirmation in [
                "yes",
                "yeah",
                "yep",
                "confirm",
                "do it"
            ]:

                try:

                    shutil.rmtree(
                        folder_path
                    )

                    speak(
                        f"The folder {folder_name} "
                        "has been deleted, Chris."
                    )

                except Exception as error:

                    print(
                        "Delete error:",
                        error
                    )

                    speak(
                        f"I couldn't delete the folder "
                        f"{folder_name}, Chris."
                    )

            else:

                speak(
                    "Okay, I won't delete it, Chris."
                )

        else:

            speak(
                f"I couldn't find the folder "
                f"{folder_name}, Chris."
            )


    # =====================================================
    # LOCK COMPUTER
    # =====================================================

    elif (
        "lock computer" in text
        or "lock the computer" in text
        or "lock my computer" in text
        or "lock pc" in text
        or "lock my pc" in text
        or "lock the pc" in text
    ):

        response = lock_computer()

        speak(response)


    # =====================================================
    # SHUTDOWN
    # =====================================================

    elif (
        "shut down computer" in text
        or "shut down the computer" in text
        or "shut down pc" in text
        or "shut down my pc" in text
        or "turn off computer" in text
        or "turn off the computer" in text
        or "turn off pc" in text
        or "turn off my pc" in text
        or "power off computer" in text
        or "power off my computer" in text
        or "power off pc" in text
        or "power off my pc" in text
    ):

        speak(
            "Are you sure you want to shut down the computer?"
        )

        confirmation = listen()

        if confirmation in [
            "yes",
            "yeah",
            "yep"
        ]:

            speak(
                "Please say confirm to continue, "
                "or cancel to stop."
            )

            final_confirmation = listen()

            if "confirm" in final_confirmation:

                response = shutdown_computer()

                speak(response)

            else:

                speak(
                    "Shutdown cancelled, Chris."
                )

        else:

            speak(
                "Shutdown cancelled, Chris."
            )


    # =====================================================
    # RESTART
    # =====================================================

    elif (
        "restart computer" in text
        or "restart the computer" in text
        or "restart pc" in text
        or "restart my pc" in text
        or "reboot computer" in text
        or "reboot the computer" in text
        or "reboot pc" in text
        or "reboot my pc" in text
    ):

        speak(
            "Are you sure you want to restart the computer?"
        )

        confirmation = listen()

        if confirmation in [
            "yes",
            "yeah",
            "yep"
        ]:

            speak(
                "Please say confirm to continue, "
                "or cancel to stop."
            )

            final_confirmation = listen()

            if "confirm" in final_confirmation:

                response = restart_computer()

                speak(response)

            else:

                speak(
                    "Restart cancelled, Chris."
                )

        else:

            speak(
                "Restart cancelled, Chris."
            )


    # =====================================================
    # CANCEL SHUTDOWN / RESTART
    # =====================================================

    elif (
        "cancel shutdown" in text
        or "cancel restart" in text
        or text == "cancel"
    ):

        response = cancel_shutdown()

        speak(response)


    
    # =====================================================
    # UNKNOWN COMMAND → NOVA BRAIN
    # =====================================================

    else:
        start_time = time.time()
        response = ask_ai(text)
        print(f"Nova AI response time: {time.time() - start_time:.2f} seconds")
        speak(response)

