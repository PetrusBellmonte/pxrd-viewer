from menutheme import register_nav_page, menutheme
from nicegui import ui
from data_sources import (
    Spectrum,
    delete_spectrum,
    edit_spectrum,
    list_available_spectra,
    ALL_ELEMENTS,
    list_used_tags,
)
import altui


@register_nav_page("/edit-spectra", display_name="Edit Spectra", favicon="✏️")
def edit_spectra_page():
    with menutheme("Edit Saved Spectra"):
        ui.label("Edit Saved Spectra").classes("text-2xl font-bold mb-4")
        spectra = list_available_spectra()
        if not spectra:
            ui.notify("No spectra available to edit.", color="info")
            return

        def update_selected_spectrum(spectrum: Spectrum):
            # Reset fields to selected spectrum
            spectrum_name.value = spectrum.name
            display_name.value = getattr(spectrum, "display_name", "")
            description.value = getattr(spectrum, "description", "")
            selected_elements.value = list(spectrum.contained_elements)
            tags.value = list(spectrum.tags)

        spectrum_names = [s.name for s in spectra]
        selected_name = ui.select(
            spectrum_names,
            label="Select a spectrum to edit",
            value=spectrum_names[0],
            on_change=lambda e: update_selected_spectrum(next(s for s in spectra if s.name == e.value)),
        ).classes("w-full")
        spectrum_name = ui.input("Spectrum name").classes("w-full")
        display_name = ui.input("Display name (optional)").classes("w-full")
        description = ui.textarea("Description").classes("w-full")
        selected_elements = ui.select(ALL_ELEMENTS, label="Contained elements", multiple=True).classes("w-full")
        tags = altui.tag_select(list(list_used_tags()), label="Tags").classes("w-full")
        # Initialize fields
        update_selected_spectrum(spectra[0])

        async def on_save():
            nonlocal spectra
            # Validate
            if not spectrum_name.value:
                ui.notify("Please enter a spectrum name.", color="negative")
                return
            if not selected_elements.value:
                ui.notify("Please select at least one element.", color="negative")
                return
            try:
                selected_spectrum = next(s for s in spectra if s.name == selected_name.value)
                new_spectrum = edit_spectrum(
                    old_spectrum=selected_spectrum,
                    new_name=spectrum_name.value,
                    contained_elements=set(selected_elements.value),
                    tags=list(tags.value),
                    description=description.value,
                    display_name=display_name.value if display_name.value else None,
                )
                spectra = list_available_spectra()
                selected_name.options = [s.name for s in spectra]
                selected_name.value = new_spectrum.name  # todo make the whole data management nicer
                tags.options = list(list_used_tags())
                ui.notify("Spectrum metadata updated!", color="positive")
            except Exception as e:
                ui.notify(f"Error updating spectrum: {e}", color="negative")

        async def on_delete():
            nonlocal spectra, spectrum_names
            try:
                selected_spectrum = next(s for s in spectra if s.name == selected_name.value)
                delete_spectrum(selected_spectrum)
                ui.notify(f"Spectrum '{selected_spectrum.name}' deleted!", color="positive")
                spectra = list_available_spectra()
                if not spectra:
                    ui.notify("No spectra available to edit.", color="info")
                    ui.navigate.reload()
                    return
                spectrum_names = [s.name for s in spectra]
                selected_name.options = spectrum_names
                selected_name.value = spectra[0].name
                tags.options = list(list_used_tags())
            except Exception as e:
                ui.notify(f"Error deleting spectrum: {e}", color="negative")

        with ui.row().classes("w-full"):
            ui.button("Save Changes", on_click=on_save, color="primary").classes("mt-4")
            ui.button("Delete Spectrum", on_click=on_delete, color="negative").classes("mt-4")
