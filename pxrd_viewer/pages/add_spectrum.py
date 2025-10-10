from menutheme import register_nav_page, menutheme
from nicegui import ui, events
from pathlib import Path
from data_sources import ALL_ELEMENTS, list_used_tags, load_raw_file, load_xyd_file, save_new_spectrum
import io
import altui

# Increase upload size limit to 5 MB (https://nicegui.io/documentation/upload#uploading_large_files)
from starlette.formparsers import MultiPartParser

MultiPartParser.spool_max_size = 1024 * 1024 * 5  # 5 MB


@register_nav_page("/add-spectrum", display_name="Add Spectrum", favicon="📈")
def add_spectrum_page():
    with menutheme("Add a New Spectrum"):
        ui.label("Add a New Spectrum").classes("text-2xl font-bold mb-4")
        DATA_DIR = Path(__file__).parent.parent / "data"
        if not DATA_DIR.exists():
            DATA_DIR.mkdir(parents=True)
        with ui.card().classes("w-full max-w-xl"):
            spectrum_name = (
                ui.input("Spectrum name (unique, no spaces)")
                .classes("w-full")
                .props(
                    'required :rules="['
                    "val => val.length <= 50 || 'Please use maximum 50 characters',"
                    "val => /^[^<>:\\\"/\\\\\\\\|?*\\\\s]+$/.test(val) || 'Name must not contain < > : \\\" / \\\\ | ? * or spaces',"  # noqa: E501
                    ']"'
                )
            )

            display_name = ui.input("Display name (optional)").classes("w-full")
            description = ui.textarea("Description").classes("w-full")
            uploaded_file_content = {"file": None}

            async def handle_upload(e: events.UploadEventArguments):
                file = e.file
                file_bytes = io.BytesIO(await file.read())
                try:
                    if file.name.endswith(".xyd"):
                        spectra_content = load_xyd_file(file_bytes)
                    elif file.name.endswith(".raw"):
                        spectra_content = load_raw_file(file_bytes)
                    else:
                        raise ValueError("Unsupported file format")
                except Exception as ex:
                    ui.notify(f"Error loading file: {ex}", color="negative")
                    uploaded_file.reset()
                    print(ex)
                    return
                uploaded_file_content["file"] = spectra_content

            uploaded_file = (
                ui.upload(
                    label="Choose a spectrum file",
                    multiple=False,
                    on_upload=handle_upload,
                    auto_upload=True,
                    max_total_size=5 * 1024 * 1024,
                )
                .props("accept=.xyd,.raw")
                .classes("w-full")
            )
            selected_elements = ui.select(
                ALL_ELEMENTS, label="Contained elements", multiple=True
            ).classes("w-full")
            tags = altui.tag_select(list(list_used_tags()), label="Tags").classes(
                "w-full"
            )

            async def on_submit():
                file = uploaded_file_content["file"]
                if not file:
                    ui.notify("Please upload a spectrum file.", color="negative")
                elif not spectrum_name.value:
                    ui.notify("Please enter a spectrum name.", color="negative")
                elif not selected_elements.value:
                    ui.notify("Please select at least one element.", color="negative")
                else:
                    save_new_spectrum(
                        name=spectrum_name.value,
                        uploaded_file=file,
                        contained_elements=set(selected_elements.value),
                        tags=tags.value,
                        description=description.value,
                        display_name=display_name.value if display_name.value else None,
                    )
                    ui.notify("Spectrum uploaded successfully!", color="positive")
                    # Manually reset all fields
                    spectrum_name.value = ""
                    await spectrum_name.run_method(
                        "resetValidation"
                    )  # it only works if execute twice???
                    display_name.value = ""
                    description.value = ""
                    uploaded_file.reset()
                    uploaded_file_content["file"] = None
                    selected_elements.value = []
                    tags.value = []
                    tags.options = list(list_used_tags())
                    await spectrum_name.run_method("resetValidation")

            ui.button("Upload Spectrum", on_click=on_submit, color="primary").classes(
                "mt-4"
            )
