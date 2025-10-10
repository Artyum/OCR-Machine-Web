import logging
import os

from config import Config
from nicegui import ui
from services import clear_all_data, download_zip, get_file_list, image_to_pdf, processor, save_upload

from .page_header import page_header


def page_index():
    async def clear_files():
        clear_all_data()
        processor.clear_files()
        refresh_processing_table()
        refresh_output_table()

    def refresh_processing_table():
        # Refresh processing table rows
        processing_table.rows = processor.get_file_list()
        processing_table.update()

    def refresh_output_table():
        # Refresh output table rows
        output_table.rows = get_file_list(dir=Config.OUTPUT_DIR)
        output_table.update()

    def upload(e):
        save_path = save_upload(e, Config.INPUT_DIR)
        if save_path:
            image_to_pdf(save_path)

    # Register callback
    processor.subscribe(lambda: (
        refresh_processing_table(),
        refresh_output_table()
    ))

    page_header(title="OCR")
    with ui.column().classes("page_column"):
        ui.label("Drop box").classes("label-header upload_label")
        ui.upload(on_upload=upload, auto_upload=True, multiple=True).props(f"accept=.pdf,{','.join(Config.SUPPORTED_IMAGE_EXTENSIONS)}").classes("upload_flield")

        ui.label("Processing list").classes("label-header table_processing_label")
        processing_table = ui.table(
            columns=[
                {"name": "name", "label": "File name", "field": "name", "align": "left"},
                {"name": "status", "label": "Status", "field": "status", "align": "left"},
                {"name": "size", "label": "Size", "field": "size", "align": "right"}
            ],
            rows=[],
            row_key="name"
        ).classes("status_table")

        ui.label("Download").classes("label-header table_finished_label")
        output_table = ui.table(
            columns=[
                {"name": "name", "label": "File name", "field": "name", "align": "left"},
                {"name": "size", "label": "Size", "field": "size", "align": "right"},
                {"name": "download", "label": "Download", "field": "download_url", "align": "center"}
            ],
            rows=[],
            row_key="name"
        ).classes("status_table")

        # Add slot for download buttons (formatted without function in template)
        output_table.add_slot('body-cell-download', '''
            <q-td :props="props">
                <a :href="props.row.download_url" download style="text-decoration: none;">
                    <q-btn flat round icon="download" color="primary" />
                </a>
            </q-td>
        ''')

        with ui.row().classes('w-full'):
            ui.button("Clear All", icon="delete", color="red", on_click=clear_files)
            ui.space()
            ui.button("Download All", icon="file_download", color="primary", on_click=lambda: download_zip(dir=Config.OUTPUT_DIR))

    # Refresh tables
    refresh_processing_table()
    refresh_output_table()
