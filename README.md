# 📄 PDF OCR Daemon

Ein plattformübergreifender Python-Daemon, der automatisch neue PDF-Dateien im Dokumente-Verzeichnis überwacht, fehlende OCR-Textebenen erkennt und mittels [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) automatisch hinzufügt.
Ergebnis: durchsuchbare PDFs – ganz ohne manuelles Zutun. ✨

---

## 🚀 Funktionen

- Automatische Überwachung des Dokumente-Verzeichnisses (plattformübergreifend)
- Erkennung von PDFs **ohne Textlayer**
- OCR mit [Tesseract](https://github.com/tesseract-ocr/tesseract) über [pytesseract](https://pypi.org/project/pytesseract/)
- Mehrsprachige Texterkennung (automatisch wählbar)
- Desktop-Benachrichtigung bei Erfolg oder Fehler (Windows, macOS, Linux)
- Optionaler Autostart beim System-Login oder als Dienst
- Saubere Log-Ausgabe und Fehlerhandling

---

## 🧩 Voraussetzungen

1. **Python 3.8+**  
   👉 [https://www.python.org/downloads/](https://www.python.org/downloads/)

2. **Tesseract OCR**  
   - **Windows:** Download unter [UB Mannheim Builds](https://github.com/UB-Mannheim/tesseract/wiki)  
   - **macOS:** `brew install tesseract`  
   - **Linux (Debian/Ubuntu):** `sudo apt install tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng`

3. **Python-Pakete installieren:**

```bash
pip install watchdog pytesseract pypdf2 pdf2image pillow plyer
```

*(Optional: `systemd-python` auf Linux für automatische Service-Erstellung)*

---

## ⚙️ Konfiguration

Standardmäßig überwacht der Daemon das Benutzer-Dokumente-Verzeichnis:
```python
Path.home() / "Documents"
```
Ein Unterordner `OCR_Watch` wird automatisch angelegt.  
Sprachen und Logfile können im Skript angepasst werden.

---

## 🔁 Automatischer Start beim System-Login

### 🪟 Windows

- **Variante 1:** Verknüpfung zu `ocr_daemon.py` oder `.bat` in:
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
```
Beispielinhalt:
```cmd
pythonw "C:\Pfad\zu\ocr_daemon.py"
```

- **Variante 2:** Registrierungseintrag
```python
import winreg, os, sys
key = winreg.HKEY_CURRENT_USER
subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg:
    winreg.SetValueEx(reg, "PDF_OCR_Daemon", 0, winreg.REG_SZ, f'pythonw "{os.path.abspath(sys.argv[0])}"')
```

### 🍏 macOS (LaunchAgent)

Datei: `~/Library/LaunchAgents/com.user.pdfocr.plist`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key> <string>com.user.pdfocr</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/local/bin/python3</string>
    <string>/Users/USERNAME/path/to/ocr_daemon.py</string>
  </array>
  <key>RunAtLoad</key> <true/>
  <key>KeepAlive</key> <true/>
  <key>StandardOutPath</key> <string>/tmp/pdfocr.log</string>
  <key>StandardErrorPath</key> <string>/tmp/pdfocr.err</string>
</dict>
</plist>
```

### 🐧 Linux (systemd)

Datei: `~/.config/systemd/user/pdfocr.service`
```ini
[Unit]
Description=PDF OCR Daemon
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/USERNAME/path/to/ocr_daemon.py
Restart=on-failure
WorkingDirectory=/home/USERNAME
StandardOutput=append:/home/USERNAME/.local/share/pdfocr.log
StandardError=append:/home/USERNAME/.local/share/pdfocr.err

[Install]
WantedBy=default.target
```
Aktivieren:
```bash
systemctl --user enable pdfocr.service
systemctl --user start pdfocr.service
```

---

## 🔔 Benachrichtigungen

Erfolg oder Fehler werden per Desktop-Notification angezeigt:

- Windows: [plyer.notification](https://plyer.readthedocs.io/en/latest/#plyer.notification.notification)
- macOS: via `osascript`
- Linux: `notify-send` (muss installiert sein)

---

## 🧠 TODOs & Ideen

- [ ] CLI-Optionen (`--once`, `--verbose`, `--no-notify`)
- [ ] Unterstützung für Passwort-geschützte PDFs
- [ ] Automatische Sprachwahl via Dateinamen oder Verzeichnisstruktur
- [ ] GUI-Tray-App mit Statusanzeige
- [ ] Dockerfile für Serverbetrieb
- [ ] WebUI zur Fortschrittsüberwachung

---

## 🧾 Lizenz

MIT License © 2025  
Created with ❤️ by Dirk & Vanessa(KI)
