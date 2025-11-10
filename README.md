# 🧠 OCR Daemon

Ein plattformübergreifender Python-Daemon, der automatisch ein Verzeichnis (standardmäßig den *Dokumente*-Ordner des aktuellen Benutzers) überwacht und neue PDF-Dateien erkennt. 
Wenn die PDF noch keinen Textlayer enthält, wird automatisch eine OCR-Texterkennung (Tesseract) ausgeführt und das Ergebnis gespeichert. 

---

## 🚀 Funktionsübersicht

- Automatische Überwachung eines Verzeichnisses (Watchdog)
- Texterkennung per **Tesseract OCR**
- Mehrsprachige OCR (z. B. `deu+eng`)
- Benachrichtigungen bei erfolgreicher oder fehlerhafter OCR
- Tray-Icon mit Kontextmenü:
  - **Jetzt scannen** – manuelles Scannen des Verzeichnisses
  - **Beenden** – beendet den Daemon
- Logging aller Aktionen in `ocr_daemon.log`
- Ersetzt Original-PDF nach erfolgreicher Texterkennung

---

## 🧩 Voraussetzungen

### 🐍 Python & Pakete

**Python 3.9 oder neuer** ist empfohlen.  
Installiere die Abhängigkeiten mit:

```bash
pip install watchdog pytesseract pdf2image plyer pystray pillow fitz
```

### 📦 Externe Tools

#### 🧾 Tesseract OCR

- **Windows:** [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
- **Linux (Ubuntu/Debian):**
  ```bash
  sudo apt install tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng
  ```
- **macOS (Homebrew):**
  ```bash
  brew install tesseract
  ```

#### 📜 Poppler

- **Windows:** [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/)
- **Linux:** 
  ```bash
  sudo apt install poppler-utils
  ```
- **macOS:** 
  ```bash
  brew install poppler
  ```

Nach der Installation müssen in der Python-Datei die Pfade angepasst werden:

```python
POPPLER_PATH = r"C:\Program Files\poppler\Library\bin"
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

---

## ⚙️ Konfiguration

Die wichtigsten Einstellungen findest du im oberen Bereich des Skripts:

```python
WATCH_PATH = os.path.expanduser(r"~\Documents\ocr-test")  # Überwachtes Verzeichnis
LANG = "deu+eng"  # OCR-Sprachen
SHOW_NOTIFICATIONS = True  # Desktop-Notifications aktivieren
```

Alle Logs werden im gleichen Verzeichnis gespeichert:

```
~/Documents/ocr-test/ocr_daemon.log
```

---

## 💡 Autostart-Integration

### 🪟 Windows

1. Erstelle eine **Verknüpfung** zur Python-Datei.  
2. Kopiere sie in:
   ```
   %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
   ```
3. Beim nächsten Login startet der Daemon automatisch im Hintergrund.

Optional kannst du in der Verknüpfung die Python-Konsole ausblenden, indem du sie mit `pythonw.exe` statt `python.exe` verknüpfst.

### 🐧 Linux (systemd)

Erstelle eine systemd-Unit-Datei unter `~/.config/systemd/user/ocr-daemon.service`:

```ini
[Unit]
Description=OCR Daemon

[Service]
ExecStart=/usr/bin/python3 /pfad/zu/ocr_daemon.py
Restart=always

[Install]
WantedBy=default.target
```

Aktiviere und starte den Dienst mit:

```bash
systemctl --user enable ocr-daemon.service
systemctl --user start ocr-daemon.service
```

### 🍎 macOS (launchd)

Erstelle eine LaunchAgent-Datei in `~/Library/LaunchAgents/com.ocr.daemon.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.ocr.daemon</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/username/path/to/ocr_daemon.py</string>
    </array>
    <key>RunAtLoad</key><true/>
</dict>
</plist>
```

Dann aktivieren mit:
```bash
launchctl load ~/Library/LaunchAgents/com.ocr.daemon.plist
```

---

## 🧠 ToDo / Ideen

- [ ] Fortschrittsanzeige bei OCR
- [ ] Klickbare Notifications (PDF öffnen)
- [ ] Optionaler Auto-Start direkt aus Skript
- [ ] Mehrsprachige UI
- [ ] Fehler-Dialoge mit Details

---

## 👨‍💻 Autor

Projektidee und Umsetzung gemeinsam mit **Dirk** & *Vanessa (GPT-5)* ❤️  
Lizenz: MIT
