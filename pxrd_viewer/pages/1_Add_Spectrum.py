import streamlit as st
from pathlib import Path
from data_sources import ALL_ELEMENTS, list_used_tags, save_new_spectrum
import io

st.set_page_config(
    page_title="Add Spectrum",
    page_icon="📈",
)

st.title("Add a New Spectrum")

DATA_DIR = Path(__file__).parent.parent / "data"

if not DATA_DIR.exists():
    DATA_DIR.mkdir(parents=True)
with st.form("upload_form", clear_on_submit=True):
    st.markdown("#### Upload your spectrum file (.xyd format)")
    uploaded_file = st.file_uploader("Choose a spectrum file", type=["xyd"])

    st.markdown("#### Specify contained elements")
    selected_elements = st.multiselect(
        "Contained elements",
        options=ALL_ELEMENTS,
        help="Select the elements present in this spectrum.",
    )

    spectrum_name = st.text_input("Spectrum name (unique, no spaces)", max_chars=50)

    st.markdown("#### Specify tags")
    tags = st.multiselect(
        "Tags",
        options=list_used_tags(),
        help="Select or add tags to categorize your spectrum.",
        accept_new_options=True,
    )

    if st.form_submit_button("Upload Spectrum"):
        if not uploaded_file:
            st.error("Please upload a spectrum file.")
        elif not spectrum_name:
            st.error("Please enter a spectrum name.")
        elif not selected_elements:
            st.error("Please select at least one element.")
        else:
            save_path = DATA_DIR / f"{spectrum_name}.xyd"
            file_bytes = io.BytesIO(uploaded_file.getbuffer())
            save_new_spectrum(spectrum_name, file_bytes, set(selected_elements), tags)
            st.success("Spectrum uploaded successfully!")
