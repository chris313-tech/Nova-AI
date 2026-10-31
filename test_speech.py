import subprocess

text = "Hello Chris. I am Nova. Windows is speaking for me."

powershell_command = f'''
Add-Type -AssemblyName System.Speech
$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
$speaker.Speak("{text}")
'''

subprocess.run(
    ["powershell", "-NoProfile", "-Command", powershell_command],
    check=True
)

print("Speech finished.")