from config import Config
from nicegui import ui
from services import get_langs

from .page_header import page_header


def page_settings():
    page_header(title="Settings")
    with ui.column().classes("page_column"):
        # Get available languages from Tesseract
        langs = get_langs()
        ui.label("Available languages: " + (", ".join(langs) if langs else "no data"))

        # Form fields
        language_input = ui.input("Language (e.g., pol, eng)", value=Config.language).classes("input_field")
        dpi_input = ui.number("Image DPI", value=Config.image_dpi, min=72, max=600).classes("input_field")
        optimize_input = ui.number("Optimization (0-3)", value=Config.optimize, min=0, max=3).classes("input_field")
        max_workers_input = ui.number("Parallel process limit", value=Config.max_workers, min=0, max=10).classes("input_field")

        # Function to save changes
        def save_handler():
            selected_lang = language_input.value.strip()

            # --- check if selected language is valid ---
            if langs and selected_lang not in langs:
                ui.notify(f"Invalid language: '{selected_lang}'. Must be one of: {', '.join(langs)}", type="negative")
                return

            Config.language = language_input.value.strip()
            Config.image_dpi = int(dpi_input.value)
            Config.optimize = int(optimize_input.value)
            Config.max_workers = int(max_workers_input.value)
            Config.save_config()
            ui.notify("Settings saved", type="positive")

        ui.button("Save", on_click=save_handler)
