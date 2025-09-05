import logging
import os
import secrets
import sys
import threading

from config import Config
from fastapi import HTTPException
from fastapi.responses import FileResponse
from nicegui import app, ui
from pages import page_convert, page_index, page_merge, page_settings
from services import DirectoryWatcher, processor
from starlette.middleware.sessions import SessionMiddleware

# Logging configuration: INFO+ level to stdout
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logging.info("OCR Machine Start")
logging.getLogger("nicegui").setLevel(logging.WARNING)

# Static files
app.add_static_files('/static', 'static', max_cache_age=3600)

# Add SessionMiddleware with a secret key
app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(32))

# Load configuration
Config.load_config()


@ui.page("/")
def index():
    page_index()


@ui.page("/merge")
def combine():
    page_merge()


@ui.page("/convert")
def convert():
    page_convert()


@ui.page("/settings")
def settings():
    page_settings()


@ui.page("/download/{filename}")
async def download_file(filename: str):
    """Secure endpoint for downloading files"""
    # Validate filename to prevent path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = os.path.join(Config.OUTPUT_DIR, filename)

    # Check if file exists
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File does not exist")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )


# File watcher
def watcher_input_handler(filepath: str):
    logging.info(f"New file detected: {filepath}")
    # Add file to processing queue
    processor.add_file(path=filepath)


watcher = DirectoryWatcher(Config.INPUT_DIR, watcher_input_handler)
watcher.start()

# Start background thread for processing loop
threading.Thread(
    target=processor.process_loop,
    daemon=True,
    name="ProcessorLoop"
).start()

# Start NiceGUI app
ui.run(
    title="OCR Machine",
    host='0.0.0.0',
    reload=False,
    binding_refresh_interval=1,
    reconnect_timeout=600,
    dark=False
)
