from nicegui import ui


def page_header(title):
    # Load custom stylesheet
    ui.add_head_html('<link rel="stylesheet" href="/static/style.css">')

    with ui.column().classes("page_column").style("gap: 0;"):
        # Main application title
        ui.label("OCR Machine").classes("main_title")

        # Navigation menu
        with ui.row().classes("menu_row"):
            ui.link("🔍 OCR", "/").classes("menu_link")
            ui.link("➕ Merge", "/merge").classes("menu_link")
            ui.link("🖼️ PDF to Image", "/convert").classes("menu_link")
            ui.space()
            ui.link("⚙️ Settings", "/settings").classes("menu_link")

        with ui.row().classes('separator'):
            ui.label(title)
