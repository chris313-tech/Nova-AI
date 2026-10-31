
Set WshShell = CreateObject("WScript.Shell")

WshShell.CurrentDirectory = "C:\Users\opare\Desktop\ok\Startups\Setups\Nova AI"

WshShell.Run """C:\Users\opare\Desktop\ok\Startups\Setups\Nova AI\.venv\Scripts\pythonw.exe"" ""C:\Users\opare\Desktop\ok\Startups\Setups\Nova AI\main.py""", 0, False
