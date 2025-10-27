from nicegui import ui


def page_header(title):
    # Load custom stylesheet
    ui.add_head_html('''
        <link rel="stylesheet" href="/static/style.css">
        <style>

        </style>
    ''')

    with ui.column().classes("page_column"):
        # Modern gradient header
        with ui.column().classes("modern-header w-full"):
            with ui.column().classes("header-content w-full"):
                # App title
                ui.label("OCR Machine").classes("app-title")

                # Navigation buttons
                with ui.row().classes("nav-container w-full"):
                    with ui.link(target="/").classes("nav-button"):
                        ui.label("🔍").classes("icon")
                        ui.label("OCR")

                    with ui.link(target="/merge").classes("nav-button"):
                        ui.label("➕").classes("icon")
                        ui.label("Merge")

                    with ui.link(target="/convert").classes("nav-button"):
                        ui.label("🖼️").classes("icon")
                        ui.label("PDF to Image")

                    with ui.link(target="/settings").classes("nav-button settings-button"):
                        ui.label("⚙️").classes("icon")
                        ui.label("Settings")

        # Page title section
        with ui.row().classes("page-title-section w-full"):
            ui.label(title).classes("page-title")
