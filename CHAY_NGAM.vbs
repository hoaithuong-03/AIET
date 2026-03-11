Set WshShell = CreateObject("WScript.Shell")
' Chay file batch o che do an (0) va khong cho ket thuc (False)
WshShell.Run "cmd.exe /c CHAY_AI.bat", 0, False
