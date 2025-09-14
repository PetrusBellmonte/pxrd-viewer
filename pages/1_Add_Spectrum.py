import streamlit as st
from pathlib import Path
from data_sources import ALL_ELEMENTS

st.set_page_config(
    page_title="Add Spectrum",
    page_icon="📈",
)

st.title("Add a New Spectrum")

DATA_DIR = Path(__file__).parent.parent / "data"

if not DATA_DIR.exists():
    DATA_DIR.mkdir(parents=True)

st.markdown("#### Upload your spectrum file (.xyd format)")
uploaded_file = st.file_uploader("Choose a spectrum file", type=["xyd"])

st.markdown("#### Specify contained elements")
selected_elements = st.multiselect(
    "Contained elements",
    options=ALL_ELEMENTS,
    help="Select the elements present in this spectrum.",
)

spectrum_name = st.text_input("Spectrum name (unique, no spaces)", max_chars=50)

if st.button("Upload Spectrum"):
    if not uploaded_file:
        st.error("Please upload a spectrum file.")
    elif not spectrum_name:
        st.error("Please enter a spectrum name.")
    elif not selected_elements:
        st.error("Please select at least one element.")
    else:
        save_path = DATA_DIR / f"{spectrum_name}.xyd"
        if save_path.exists():
            st.error("A spectrum with this name already exists.")
        else:
            # Save the uploaded file
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            # Optionally, save metadata (elements) in a separate file
            meta_path = DATA_DIR / f"{spectrum_name}.meta"
            with open(meta_path, "w") as f:
                f.write(",".join(selected_elements))
