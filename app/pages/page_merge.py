import logging
import os
from pathlib import Path

from config import Config
from nicegui import ui
from PyPDF2 import PdfMerger
from services import get_file_list, image_to_pdf, move_files

from .page_header import page_header


def page_merge():
    output_filename = "Combined_document.pdf"

    def upload(file):
        if not file:
            ui.notify("Failed to upload file", type="negative")
            return

        # Save uploaded file
        save_path = os.path.join(Config.MERGE_DIR, file.name)
        with open(save_path, "wb") as f:
            f.write(file.content.read())  # here file.content is a BytesIO stream

        size = os.path.getsize(filename=save_path)
        msg = f"File saved: {file.name} ({size / 1024 / 1024:.2f} MB)"
        ui.notify(msg, type="positive")
        logging.info(msg)

        image_to_pdf(save_path)

        # Refresh processing list
        refresh_processing_table()

    def refresh_processing_table():
        # Get files
        files = get_file_list(dir=Config.MERGE_DIR)

        # filter out unwanted file by name
        # files = [f for f in files if f["name"] != output_filename]

        # Sort alphabetically by file name
        files_sorted = sorted(files, key=lambda f: f["name"].lower())

        # Add numbering column
        rows = []
        for i, file in enumerate(files_sorted, start=1):
            rows.append({
                "index": i,             # new column with row number
                "name": file["name"],
                "size": file["size"]
            })

        # Update table data
        processing_table.rows = rows
        processing_table.update()

    def merge():
        try:
            files = get_file_list(dir=Config.MERGE_DIR)
            pdf_files = sorted(
                [os.path.join(Config.MERGE_DIR, f["name"]) for f in files if f["name"].endswith(".pdf") and f["name"] != output_filename]
            )

            if not pdf_files:
                ui.notify("No PDF files to merge", type="warning")
                return

            output_path = os.path.join(Config.MERGE_DIR, output_filename)

            merger = PdfMerger()
            for pdf in pdf_files:
                merger.append(pdf)
            merger.write(output_path)
            merger.close()

            msg = f"Merged {len(pdf_files)} files into {output_filename}"
            logging.info(msg)
            ui.notify(msg, type="positive")

            # Delete processed PDFs
            for pdf in pdf_files:
                try:
                    os.remove(pdf)
                    logging.info(f"Deleted source file: {pdf}")
                except Exception as e:
                    logging.error(f"Failed to delete {pdf}: {e}")

            refresh_processing_table()

        except Exception as e:
            logging.error(f"Error during PDF merge: {e}")
            ui.notify(f"Error: {e}", type="negative")

    def download():
        file_path = Path(Config.MERGE_DIR) / output_filename

        try:
            if not file_path.exists():
                ui.notify(f"File '{output_filename}' not found. Please merge first.", type="warning")
                logging.warning(f"Download failed: {file_path} does not exist")
                return

            ui.download(src=file_path, filename=output_filename)
            logging.info(f"Download started for: {file_path}")

        except Exception as e:
            msg = f"Error while preparing download: {e}"
            logging.error(msg)
            ui.notify(msg, type="negative")

    def move_to_ocr():
        filelist = move_files(src_dir=Config.MERGE_DIR, dst_dir=Config.INPUT_DIR, extension=".pdf")
        if len(filelist) == 0:
            ui.notify("No PDF files to move", type="warning")
        else:
            ui.navigate.to("/")

    page_header(title="Merge")
    with ui.column().classes("page_column"):
        ui.label("Drop box").classes("label-header upload_label")
        ui.upload(on_upload=upload, auto_upload=True, multiple=True).props(f"accept=.pdf,{','.join(Config.SUPPORTED_IMAGE_EXTENSIONS)}").classes("upload_flield")

        ui.label("Merge list").classes("label-header table_processing_label")
        processing_table = ui.table(
            columns=[
                {"name": "index", "label": "Order", "field": "index", "align": "center"},
                {"name": "name", "label": "File name", "field": "name", "align": "left"},
                {"name": "size", "label": "Size", "field": "size", "align": "right"},
            ],
            rows=[],
            row_key="name"
        ).classes("status_table")

        with ui.row().classes("w-full"):
            ui.button("Merge", icon="merge_type", color="primary", on_click=merge)
            ui.space()
            ui.button("Send all to OCR", icon="forward", color="primary", on_click=move_to_ocr)
            ui.space()
            ui.button("Download All", icon="download", color="primary", on_click=download)

    refresh_processing_table()
