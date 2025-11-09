import os
import time
import fitz
import pytesseract
import shutil
import tempfile
import threading
import signal
from pdf2image import convert_from_path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from plyer import notification


# === Einstellungen ===
WATCH_PATH = os.path.expanduser(r"~\\Documents\\ocr-test")  # <--- dynamisch für jeden Benutzer
POPPLER_PATH = r"C:\\Program Files\\poppler\\Library\\bin"  # <--- Pfad zu poppler/bin
TESSERACT_CMD = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"  # <--- Pfad zu tesseract.exe
LANG = "deu+eng"  # OCR-Sprachen

# Stelle sicher, dass der Watch-Ordner existiert
os.makedirs(WATCH_PATH, exist_ok=True)
LOGFILE = os.path.join(WATCH_PATH, "ocr_daemon.log")
SHOW_NOTIFICATIONS = True  # Desktop-Notifications aktivieren
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


# === Logging und Benachrichtigung ===
def log(msg):
    ts = time.strftime("[%Y-%m-%d %H:%M:%S]")
    print(ts, msg)
    os.makedirs(os.path.dirname(LOGFILE), exist_ok=True)
    with open(LOGFILE, "a", encoding="utf-8") as f:
        f.write(f"{ts} {msg}\n")


def notify(title, message):
    """Cross-platform desktop notification."""
    if SHOW_NOTIFICATIONS:
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=5,
                app_name="OCR-Daemon"
            )
        except Exception as e:
            log(f"[WARN] Notification failed: {e}")


# === Cache zur Doppelverarbeitungs-Vermeidung ===
processed_files = {}

def recently_processed(path, delay=30):
    """Verhindert doppelte Verarbeitung derselben Datei."""
    now = time.time()
    if path in processed_files and now - processed_files[path] < delay:
        return True
    processed_files[path] = now
    threading.Timer(delay, lambda: processed_files.pop(path, None)).start()
    return False


# === Kernfunktionen ===
def has_text_layer(pdf_path):
    """Prüft, ob die PDF bereits eine Textebene enthält."""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                if page.get_text("text").strip():
                    return True
        return False
    except Exception as e:
        log(f"[ERROR] Kann Textlayer in {pdf_path} nicht prüfen: {e}")
        notify("Fehler bei PDF", f"{os.path.basename(pdf_path)} konnte nicht gelesen werden.")
        # Datei überspringen, damit kein Endlos-OCR-Versuch
        return True


def ocr_pdf(pdf_path, lang=LANG):
    """Führt OCR durch und ersetzt die Datei bei Erfolg."""
    log(f"[INFO] OCR start: {pdf_path}")
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            images = convert_from_path(
                pdf_path,
                dpi=300,
                output_folder=tmpdir,
                poppler_path=POPPLER_PATH
            )
            ocr_pages = []

            for i, img in enumerate(images, start=1):
                log(f"  -> OCR page {i}/{len(images)}")
                pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, lang=lang, extension='pdf')
                page_path = os.path.join(tmpdir, f"page_{i}.pdf")
                with open(page_path, "wb") as f:
                    f.write(pdf_bytes)
                ocr_pages.append(page_path)

            new_pdf_path = os.path.join(tmpdir, "ocr_output.pdf")
            with fitz.open() as new_doc:
                for p in ocr_pages:
                    with fitz.open(p) as sp:
                        new_doc.insert_pdf(sp)
                new_doc.save(new_pdf_path)

            if os.path.getsize(new_pdf_path) > 0:
                shutil.move(new_pdf_path, pdf_path)
                msg = f"OCR erfolgreich abgeschlossen: {os.path.basename(pdf_path)}"
                log(f"  ✅ {msg}")
                notify("OCR abgeschlossen", msg)
            else:
                log(f"  ⚠️ Leeres OCR-Ergebnis bei {pdf_path}")
        except Exception as e:
            log(f"[ERROR] OCR fehlgeschlagen für {pdf_path}: {e}")
            notify("Fehler bei OCR", f"{os.path.basename(pdf_path)} konnte nicht verarbeitet werden.")


# === Watchdog-Event-Handler ===
class PDFHandler(FileSystemEventHandler):
    """Reagiert auf neue oder geänderte PDF-Dateien."""

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(".pdf"):
            time.sleep(2)
            self.process(event.src_path)

    def on_modified(self, event):
        if not event.is_directory and event.src_path.lower().endswith(".pdf"):
            time.sleep(2)
            self.process(event.src_path)

    def process(self, path):
        if recently_processed(path):
            return
        log(f"[EVENT] Neue oder geänderte Datei: {path}")
        if not has_text_layer(path):
            ocr_pdf(path)
        else:
            log(f"[SKIP] Bereits Text vorhanden: {path}")


# === Haupt-Daemon ===
def run_daemon():
    log(f"🚀 OCR Daemon gestartet – überwacht: {WATCH_PATH}")
    notify("OCR-Daemon gestartet", f"Überwacht: {WATCH_PATH}")
    event_handler = PDFHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_PATH, recursive=True)
    observer.start()

    # Signal-Handler für sauberen Exit
    def stop_daemon(sig, frame):
        log("🛑 OCR Daemon beendet (Signal empfangen).")
        notify("OCR-Daemon beendet", "Überwachung gestoppt.")
        observer.stop()

    signal.signal(signal.SIGINT, stop_daemon)
    signal.signal(signal.SIGTERM, stop_daemon)

    try:
        while observer.is_alive():
            time.sleep(5)
    except KeyboardInterrupt:
        stop_daemon(None, None)

    observer.join()


if __name__ == "__main__":
    run_daemon()
