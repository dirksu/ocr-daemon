import os
import time
import fitz
import pytesseract
import shutil
import tempfile
from pathlib import Path
from pdf2image import convert_from_path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from plyer import notification


# === Dynamischer Dokumente-Pfad ===
def get_documents_dir():
    home = Path.home()
    docs = None

    # macOS / Linux
    if (home / "Documents").exists():
        docs = home / "Documents"
    # Windows (englisch oder lokalisiert)
    elif (home / "Documents").exists():
        docs = home / "Documents"
    elif (home / "Dokumente").exists():
        docs = home / "Dokumente"
    else:
        docs = home / "Documents"
        docs.mkdir(exist_ok=True)

    return docs


WATCH_PATH = get_documents_dir() / "OCR_Watch"  # Unterordner anlegen
WATCH_PATH.mkdir(exist_ok=True)

LANG = "deu+eng"
LOGFILE = WATCH_PATH / "ocr_daemon.log"
SHOW_NOTIFICATIONS = True


# === Hilfsfunktionen ===
def log(msg):
    ts = time.strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{ts} {msg}"
    print(line)
    with open(LOGFILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def notify(title, message, icon=None):
    if not SHOW_NOTIFICATIONS:
        return
    try:
        notification.notify(
            title=title,
            message=message,
            timeout=7,
            app_name="OCR-Daemon",
            app_icon=icon or None
        )
    except Exception as e:
        log(f"[WARN] Notification failed: {e}")


def has_text_layer(pdf_path):
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                if page.get_text("text").strip():
                    return True
        return False
    except Exception as e:
        log(f"[ERROR] Textprüfung fehlgeschlagen ({pdf_path}): {e}")
        notify("Fehler bei Textprüfung", f"{os.path.basename(pdf_path)} konnte nicht gelesen werden.")
        return False


def ocr_pdf(pdf_path, lang=LANG):
    log(f"[INFO] OCR gestartet: {pdf_path}")
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            images = convert_from_path(pdf_path, dpi=300, output_folder=tmpdir)
            if not images:
                raise RuntimeError("Keine Seiten im PDF gefunden")

            ocr_pages = []
            for i, img in enumerate(images, start=1):
                log(f"  -> OCR Seite {i}/{len(images)}")
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
                msg = f"OCR abgeschlossen: {os.path.basename(pdf_path)}"
                log(f"  ✅ {msg}")
                notify("OCR erfolgreich", msg)
            else:
                raise RuntimeError("OCR-Ausgabe war leer.")
        except Exception as e:
            log(f"[ERROR] OCR fehlgeschlagen ({pdf_path}): {e}")
            notify(
                "❌ OCR-Fehler",
                f"{os.path.basename(pdf_path)} konnte nicht verarbeitet werden.\nFehler: {e}"
            )


class PDFHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(".pdf"):
            time.sleep(2)
            self.process(event.src_path)

    def on_modified(self, event):
        if not event.is_directory and event.src_path.lower().endswith(".pdf"):
            time.sleep(2)
            self.process(event.src_path)

    def process(self, path):
        log(f"[EVENT] Neue oder geänderte Datei: {path}")
        if not has_text_layer(path):
            ocr_pdf(path)
        else:
            log(f"[SKIP] Bereits Text vorhanden: {path}")


def run_daemon():
    log(f"🚀 OCR-Daemon gestartet – überwacht: {WATCH_PATH}")
    notify("OCR-Daemon gestartet", f"Überwacht: {WATCH_PATH}")
    event_handler = PDFHandler()
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_PATH), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
        log("🛑 OCR-Daemon manuell beendet.")
        notify("OCR-Daemon beendet", "Überwachung gestoppt.")
    observer.join()


if __name__ == "__main__":
    run_daemon()
