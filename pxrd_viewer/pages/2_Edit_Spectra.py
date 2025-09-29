import streamlit as st
from data_sources import delete_spectrum, list_available_spectra, ALL_ELEMENTS, list_used_tags, save_new_spectrum
from pathlib import Path
import io
import yaml

st.set_page_config(
    page_title="Edit Spectra",
    page_icon="✏️",
)

st.title("Edit Saved Spectra")

spectra = list_available_spectra()
if not spectra:
    st.info("No spectra available to edit.")
    st.stop()

spectrum_names = [s.name for s in spectra]
selected_name = st.selectbox("Select a spectrum to edit", spectrum_names)

spectrum = next(s for s in spectra if s.name == selected_name)

st.markdown("#### Edit spectrum metadata")
new_name = st.text_input("Spectrum name", value=spectrum.name)
new_elements = st.multiselect(
    "Contained elements",
    options=ALL_ELEMENTS,
    default=list(spectrum.contained_elements),
)
new_tags = st.multiselect("Tags", options=list_used_tags(), default=list(spectrum.tags), accept_new_options=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("Save Changes", use_container_width=True):
        # Update meta file only (not spectrum data)
        meta_file = spectrum.source_file.parent / f"{spectrum.name}.meta"
        new_meta_file = spectrum.source_file.parent / f"{new_name}.meta"
        meta_data = {
            "name": new_name,
            "source_file": spectrum.source_file.name,
            "contained_elements": list(new_elements),
            "tags": list(new_tags),
        }
        # Remove old meta if name changed
        if new_name != spectrum.name and meta_file.exists():
            meta_file.unlink()
        with open(new_meta_file, "w") as f:
            yaml.dump(meta_data, f)
        st.success("Spectrum metadata updated!")
        st.experimental_rerun()

with col2:
    if st.button("Delete Spectrum", type="primary", help="Delete this spectrum", use_container_width=True):
        st.markdown(
            "<style>.stButton button {background-color: #d9534f; color: white;}</style>",
            unsafe_allow_html=True,
        )
        delete_spectrum(spectrum)
        st.success(f"Spectrum '{spectrum.name}' deleted!")
        st.rerun()