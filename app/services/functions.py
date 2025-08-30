import io
import logging
import os
import shutil
import subprocess
import zipfile
from pathlib import Path

import img2pdf
from config import Config
from nicegui import ui


def get_langs():
    """Return a list of languages supported by Tesseract OCR"""
    try:
        logging.info("Fetching OCR languages")
        result = subprocess.run(
            ["tesseract", "--list-langs"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.splitlines()[1:] if result.returncode == 0 else []
    except Exception as e:
        logging.warning(f"Could not fetch language list: {e}")
        return []


def get_file_list(dir):
    """Return list of output files available for download"""
    files = [
        {
            "name": f,
            "size": format_size(os.path.getsize(os.path.join(dir, f))),
            "download_url": f"/download/{f}"  # URL to secure download endpoint
        }
        for f in os.listdir(dir)
        if os.path.isfile(os.path.join(dir, f))
    ]
    return files


def convert_image(file_path: str):
    """Convert single image file to PDF in the same directory"""

    if not file_path.lower().endswith(Config.SUPPORTED_IMAGE_EXTENSIONS):
        return

    pdf_name = os.path.splitext(os.path.basename(file_path))[0] + ".pdf"
    pdf_path = os.path.join(os.path.dirname(file_path), pdf_name)

    try:
        with open(pdf_path, "wb") as f:
            f.write(img2pdf.convert(file_path))

        os.remove(file_path)
        logging.info(f"Converted and removed original: {file_path}")
        ui.notify(f"Image converted: {pdf_name}", type="positive")

    except Exception as e:
        logging.error(f"Failed to convert '{file_path}': {e}")
        ui.notify(f"Error converting {os.path.basename(file_path)}", type="negative")


def format_size(size_in_bytes: int) -> str:
    """Convert bytes into human-readable B, KB or MB format"""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 ** 2:
        return f"{size_in_bytes / 1024:.2f} KB"
    else:
        return f"{size_in_bytes / (1024 ** 2):.2f} MB"


def clear_all_data():
    """Clear all files from input and output directories"""
    dirs = [Config.INPUT_DIR, Config.OUTPUT_DIR, Config.MERGE_DIR]
    for directory in dirs:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Delete file or symlink
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Delete subdirectory
            except Exception as e:
                logging.error(f"Error deleting {file_path}: {e}")

        logging.info(f"Directory {directory} has been cleared")

    ui.notify("Cleared", type="positive")


async def download_zip(dir):
    """Create and download a ZIP archive with all files"""
    # Check if output directory exists and contains files
    if not os.path.exists(dir) or not any(Path(dir).iterdir()):
        ui.notify("No files to download", type="warning")
        return

    # Create ZIP archive in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in Path(dir).iterdir():
            if file_path.is_file():
                zip_file.write(file_path, file_path.name)

    zip_buffer.seek(0)
    # Trigger download
    ui.download(zip_buffer.getvalue(), 'all_files.zip', 'application/zip')
    ui.notify("Downloading all files as ZIP archive", type="info")


def move_files(src_dir: str, dst_dir: str, extension: str = ".pdf"):
    """
    Move all files with the given extension from src_dir to dst_dir.

    Args:
        src_dir (str): Directory with files to move.
        dst_dir (str): Target directory for files.
        extension (str): File extension filter (e.g. ".pdf", ".jpg").

    Returns:
        int: Number of moved files.
    """
    # Normalize extension (ensure it starts with ".")
    if not extension.startswith("."):
        extension = "." + extension

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)  # Create target dir if it does not exist

    file_list = []

    for filename in os.listdir(src_dir):
        if filename.lower().endswith(extension.lower()):
            src_path = os.path.join(src_dir, filename)
            dst_path = os.path.join(dst_dir, filename)

            try:
                shutil.move(src_path, dst_path)
                file_list.append(filename)
            except Exception as e:
                print(f"Failed to move {filename}: {e}")

    return file_list
