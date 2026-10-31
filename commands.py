import subprocess


def open_calculator():
    subprocess.Popen("calc.exe")
    return "Calculator is open, Chris."


def open_notepad():
    subprocess.Popen("notepad.exe")
    return "Notepad is open, Chris."


def open_chrome():
    subprocess.Popen("start chrome", shell=True)
    return "Chrome is open, Chris."


def open_settings():
    subprocess.Popen("start ms-settings:", shell=True)
    return "Settings is open, Chris."


def open_file_explorer():
    subprocess.Popen("explorer.exe")
    return "File Explorer is open, Chris."


def open_task_manager():
    subprocess.Popen("taskmgr.exe")
    return "Task Manager is open, Chris."


def open_command_prompt():
    subprocess.Popen("cmd.exe")
    return "Command Prompt is open, Chris."


def open_control_panel():
    subprocess.Popen("control.exe")
    return "Control Panel is open, Chris."


def open_vscode():
    subprocess.Popen("code")
    return "VS Code is open, Chris."


def open_downloads():
    subprocess.Popen("explorer.exe shell:Downloads")
    return "Downloads is open, Chris."


def open_documents():
    subprocess.Popen("explorer.exe shell:Personal")
    return "Documents is open, Chris."


def open_desktop():
    subprocess.Popen("explorer.exe shell:Desktop")
    return "Desktop is open, Chris."


def open_pictures():
    subprocess.Popen("explorer.exe shell:Pictures")
    return "Pictures is open, Chris."


def open_music():
    subprocess.Popen("explorer.exe shell:MyMusic")
    return "Music is open, Chris."


def open_videos():
    subprocess.Popen("explorer.exe shell:MyVideos")
    return "Videos is open, Chris."


def lock_computer():
    subprocess.Popen("rundll32.exe user32.dll,LockWorkStation")
    return "Your computer is locked, Chris."


def shutdown_computer():
    subprocess.Popen("shutdown /s /t 20", shell=True)
    return "The computer will shut down in 20 seconds, Chris."


def restart_computer():
    subprocess.Popen("shutdown /r /t 20", shell=True)
    return "The computer will restart in 20 seconds, Chris."


def cancel_shutdown():
    subprocess.Popen("shutdown /a", shell=True)
    return "The shutdown or restart has been cancelled, Chris."


import os


def create_folder(folder_name, location):
    path = os.path.join(location, folder_name)

    if os.path.exists(path):
        return f"The folder {folder_name} already exists, Chris."

    os.makedirs(path)
    return f"I created the folder {folder_name}, Chris."


def open_folder(folder_name, location=None):
    import os
    import subprocess

    if location is None:
        location = os.path.join(
            os.path.expanduser("~"),
            "Desktop"
        )

    folder_path = os.path.join(location, folder_name)

    if not os.path.exists(folder_path):
        return f"I couldn't find the folder {folder_name}, Chris."

    subprocess.Popen(
        ["explorer.exe", folder_path]
    )

    return f"I opened the folder {folder_name}, Chris."


def open_file(file_name):
    import os
    import subprocess

    search_locations = [
        os.path.join(os.path.expanduser("~"), "Desktop"),
        os.path.join(os.path.expanduser("~"), "Documents"),
        os.path.join(os.path.expanduser("~"), "Downloads"),
        os.path.join(os.path.expanduser("~"), "Pictures"),
        os.path.join(os.path.expanduser("~"), "Music"),
        os.path.join(os.path.expanduser("~"), "Videos")
    ]

    for location in search_locations:

        file_path = os.path.join(location, file_name)

        if os.path.isfile(file_path):
            os.startfile(file_path)
            return f"I opened {file_name}, Chris."

    return f"I couldn't find {file_name}, Chris."