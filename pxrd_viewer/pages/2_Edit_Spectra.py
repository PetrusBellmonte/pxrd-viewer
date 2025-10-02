import streamlit as st
from data_sources import delete_spectrum, edit_spectrum, list_available_spectra, ALL_ELEMENTS, list_used_tags
from pathlib import Path
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
        # Use edit_spectrum from data_sources
        try:
            edit_spectrum(
                old_spectrum=spectrum,
                new_name=new_name,
                contained_elements=set(new_elements),
                tags=list(new_tags),
            )
            st.success("Spectrum metadata updated!")
        except Exception as e:
            st.error(f"Error updating spectrum: {e}")

with col2:
    if st.button("Delete Spectrum", type="primary", help="Delete this spectrum", use_container_width=True):
        st.markdown(
            "<style>.stButton button {background-color: #d9534f; color: white;}</style>",
            unsafe_allow_html=True,
        )
        try:
            delete_spectrum(spectrum)
            st.success(f"Spectrum '{spectrum.name}' deleted!")
        except Exception as e:
            st.error(f"Error deleting spectrum: {e}")