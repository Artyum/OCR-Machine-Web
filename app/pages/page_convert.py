import logging
import os
from pathlib import Path

from config import Config
from nicegui import ui
from services import download_zip, get_file_list, pdf_to_jpg

from .page_header import page_header


def page_convert():
    def upload(file):
        if not file:
            ui.notify("Failed to upload file", type="negative")
            return

        # Save uploaded file
        save_path = os.path.join(Config.CONVERT_DIR, file.name)
        with open(save_path, "wb") as f:
            f.write(file.content.read())  # here file.content is a BytesIO stream

        size = os.path.getsize(filename=save_path)
        msg = f"File saved: {file.name} ({size / 1024 / 1024:.2f} MB)"
        ui.notify(msg, type="positive")
        logging.info(msg)

        # Start conversion
        convert()

        # Refresh processing list
        refresh_processing_table()

    def convert():
        """
        Processes all PDF files from the Config.CONVERT directory and converts them to JPG.
        """
        input_dir = Path(Config.CONVERT_DIR)

        pdf_files = list(input_dir.glob("*.pdf"))
        if not pdf_files:
            logging.info(f"No PDF files found in {input_dir}")
            return

        for pdf in pdf_files:
            try:
                logging.info(f"Converting: {pdf}")
                pdf_to_jpg(str(pdf), output_dir=Config.CONVERT_DIR)
                os.remove(pdf)
            except Exception as e:
                logging.warning(f"Error converting {pdf}: {e}")

    def refresh_processing_table():
        # Get files
        files = get_file_list(dir=Config.CONVERT_DIR)

        # Sort alphabetically by file name
        files_sorted = sorted(files, key=lambda f: f["name"].lower())

        # Add numbering column
        rows = []
        for file in files_sorted:
            rows.append({"name": file["name"], "size": file["size"]})

        # Update table data
        processing_table.rows = rows
        processing_table.update()

    page_header(title="PDF to Image")
    with ui.column().classes("page_column"):
        ui.label("Drop box").classes("label-header upload_label")
        ui.upload(on_upload=upload, auto_upload=True, multiple=True).props("accept=.pdf").classes("upload_flield")

        ui.label("Image list").classes("label-header table_processing_label")
        processing_table = ui.table(
            columns=[
                {"name": "name", "label": "File name", "field": "name", "align": "left"},
                {"name": "size", "label": "Size", "field": "size", "align": "right"},
            ],
            rows=[],
            row_key="name"
        ).classes("status_table")

        with ui.row().classes("w-full"):
            ui.space()
            ui.button("Download All", icon="download", color="primary", on_click=lambda: download_zip(dir=Config.CONVERT_DIR))

    refresh_processing_table()
