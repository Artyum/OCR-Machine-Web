import logging
import os
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from enum import Enum

from config import Config

from .functions import format_size


class Status(Enum):
    """Status values used during file processing"""
    NEW = "New"
    WAITING = "Waiting"
    PROCESSING = "Processing"
    DONE = "Done"
    ERROR = "Error"


class Processor:
    """Processor manages the OCR workflow for input files."""

    def __init__(self):
        # List of dicts: {name, path, status, size}
        self.files = []
        self.lock = threading.Lock()
        self._callbacks = []  # list of subscribed functions

    def subscribe(self, callback):
        """UI can register a callback for updates"""
        self._callbacks.append(callback)

    def _notify(self):
        """Call all registered callbacks"""
        for cb in self._callbacks:
            try:
                cb()
            except Exception as e:
                logging.error(f"Callback error: {e}")

    def add_file(self, path: str):
        """Add a new file to the processing queue"""
        if not os.path.exists(path) or not path.lower().endswith('.pdf'):
            return

        filename = os.path.basename(path)
        c = 0
        while True:
            size = os.path.getsize(path)
            if size > 0:
                break
            time.sleep(0.1)
            c -= 1
            if c <= 0:
                logging.error(msg=f"Nie uało się załadować pliku {filename}")
                return

        # logging.info(f"PATH={path}")
        # logging.info(f"SIZE={size}")
        # logging.info(f"NAME={filename}")

        with self.lock:
            self.files.append({
                "name": filename,
                "path": path,
                "status": Status.NEW,
                "size": format_size(size)
            })
        self._notify()  # notify UI about new file

    def clear_files(self):
        """Clear the internal file list"""
        with self.lock:
            self.files.clear()

    def get_file_list(self):
        """Return current file list without DONE files"""
        with self.lock:
            return [f for f in self.files if f.get("status") != Status.DONE]

    def process_loop(self, max_workers=3):
        """Main loop: continuously scans for new files and submits them to workers"""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            while True:
                file_to_process = None
                with self.lock:
                    for f in self.files:
                        if f["status"] == Status.NEW:
                            f["status"] = Status.WAITING
                            file_to_process = f
                            break

                if file_to_process:
                    executor.submit(self.process_file, file_to_process)
                else:
                    time.sleep(1)

    def process_file(self, file_to_process: dict):
        """Process a single file with OCR"""
        if not os.path.exists(file_to_process["path"]):
            with self.lock:
                file_to_process["status"] = Status.ERROR
            return

        with self.lock:
            file_to_process["status"] = Status.PROCESSING
        self._notify()  # status changed

        try:
            output_path = self.run_ocr(file_path=file_to_process["path"])
        except Exception:
            with self.lock:
                file_to_process["status"] = Status.ERROR
            self._notify()
            return

        if output_path and os.path.exists(output_path):
            try:
                size_after = os.path.getsize(output_path)
            except OSError:
                size_after = 0
            with self.lock:
                file_to_process["size_after"] = size_after
                file_to_process["output_path"] = output_path
                file_to_process["status"] = Status.DONE
            self._notify()

    def run_ocr(self, file_path: str):
        """Run OCRmyPDF on the given file"""
        logging.info(f"Processing new file: {file_path}")

        Config.load_config()
        ocr_output_path = os.path.join(Config.OUTPUT_DIR, os.path.basename(file_path))
        # Optional text extraction path (disabled):
        # text_output_path = os.path.join(Config.OUTPUT_DIR, os.path.splitext(os.path.basename(file_path))[0] + ".txt")

        command = [
            "ocrmypdf",
            "--image-dpi", str(Config.image_dpi),
            "--optimize", str(Config.optimize),
            "--tesseract-oem", "1",
            "--clean",
            "--output-type", "pdfa-2",
            "--redo-ocr",
            "-l", str(Config.language),
            file_path,
            ocr_output_path,
        ]
        logging.info(f"Command: {" ".join(command)}")

        try:
            result = subprocess.run(command, capture_output=True, text=True)
            os.remove(file_path)

            if result.returncode != 0:
                logging.error(f"OCRmyPDF failed ({result.returncode}) for {file_path}: {result.stderr}")
                return None

            # Optional: text extraction (disabled)
            # text_result = subprocess.run(["pdftotext", "-layout", ocr_output_path, text_output_path], capture_output=True, text=True)
            # if text_result.returncode != 0:
            #     logging.warning(f"pdftotext failed for {ocr_output_path}: {text_result.stderr}")

            logging.info(f"Processed successfully: {file_path}")
            return ocr_output_path

        except Exception as e:
            logging.error(f"Unexpected error processing {file_path}: {e}")
            return None


# Global processor instance
processor = Processor()
