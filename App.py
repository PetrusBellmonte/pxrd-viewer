from dataclasses import dataclass
import streamlit as st
import plotly.graph_objects as go
from data_sources import list_available_spectra, Spectrum


@dataclass
class Line:
    spectrum: Spectrum
    color: str
    opacity: float
    dash: str
    width: float
    title: str = None
    can_be_deleted: bool = True
    inverse: bool = True

    @classmethod
    def from_spectrum(
        cls,
        spectrum: Spectrum,
        color: str = "#0000FF",
        opacity: float = 0.8,
        dash: str = "solid",
        width: int = 2.0,
        **kwargs,
    ):
        return cls(
            spectrum=spectrum,
            color=color,
            opacity=opacity,
            dash=dash,
            width=width,
            **kwargs,
        )


st.set_page_config(page_title="Hello", page_icon="📈")
st.html("""
    <style>
        .stAppDeployButton {display:none;}
    </style>
""")
st.title("Spectrum Viewer")
st.sidebar.header("Configuration")

# Load spectra from data_sources
spectra = list_available_spectra()
spectrum_names = [s.name for s in spectra]

# Session state for spectra in view and rotation element
if "active_lines" not in st.session_state:
    st.session_state.active_lines = []
if "rotation_line" not in st.session_state:
    st.session_state.rotation_line = None

plot_slot = st.empty()  # Placeholder for the plot

# Spectrum selection above the plot
selected_spectrum = st.sidebar.selectbox("Select a spectrum to view", spectrum_names)
selected_obj = next(s for s in spectra if s.name == selected_spectrum)

if "selected_line" not in st.session_state:
    st.session_state.selected_line = Line.from_spectrum(
        selected_obj,
        color="#FF0000",
        can_be_deleted=False,
        title="(Selected)",
        inverse=False,
    )
else:
    st.session_state.selected_line.spectrum = selected_obj


def next_spectrum(spectrum: Spectrum | None = None) -> Spectrum:
    """
    Get the next fitting spectrum in the list, or the first one if None is given.

    @param spectrum: The current spectrum to find the next of.
    @return: The next spectrum in the list, or the first one if None is given.
    """
    if spectrum is None:
        return spectra[0]
    for i, s in enumerate(spectra):
        if s == spectrum:
            return spectra[(i + 1) % len(spectra)]


# Features for the rotating through spectra
rotate_control_location = st.sidebar
# Controls for the rotation element (if not enabled)
if not st.session_state.rotation_line:
    potential_interface = rotate_control_location.empty()
    if potential_interface.button("Activate Spectrum Rotation"):
        st.session_state.rotation_line = Line.from_spectrum(
            next_spectrum(), can_be_deleted=False, title="(Rot)"
        )
        potential_interface.empty()
# Controls for the rotation element (if enabled)
if st.session_state.rotation_line:
    potential_interface = rotate_control_location.empty()
    col1, col2, col3 = potential_interface.columns(3)
    if col1.button("Delete", key="rotation_delete"):
        st.session_state.rotation_line = None
    if col2.button("Next", key="rotation_next"):
        st.session_state.rotation_line.spectrum = next_spectrum(
            st.session_state.rotation_line.spectrum
        )
    if col3.button("Pin", key="rotation_pin"):
        st.session_state.rotation_line.title = None
        st.session_state.active_lines.append(st.session_state.rotation_line)
        st.session_state.rotation_line = None
    if not st.session_state.rotation_line:  # Clear if deleted or pinned
        potential_interface.empty()
        if potential_interface.button("Activate Rotation Element"):
            pass


# List all active lines including selected and rotation
def all_active_lines():
    yield st.session_state.selected_line
    if st.session_state.rotation_line:
        yield st.session_state.rotation_line
    yield from st.session_state.active_lines


# Line-Appearance-Configuration-Cards for each displayed spectrum
graph_appearance_location = st.sidebar
graph_appearance_location.header("Spectra in View")
for line in all_active_lines():
    title = line.spectrum.name
    if line.title:
        title = f"{line.title} {title}"
    potential_interface = graph_appearance_location.empty()
    with potential_interface.expander(title):
        line.color = st.color_picker("Color", line.color, key=f"color_{id(line)}")
        line.opacity = st.slider(
            "Opacity", 0.0, 1.0, line.opacity, 0.05, key=f"opacity_{id(line)}"
        )
        line.dash = st.selectbox(
            "Line style",
            ["solid", "dot", "dash", "longdash", "dashdot", "longdashdot"],
            index=0,
            key=f"dash_{id(line)}",
        )
        line.width = st.slider(
            "Stroke width", 0.5, 10.0, line.width, 0.5, key=f"width_{id(line)}"
        )
        if st.button("Delete", key=f"delete_{id(line)}"):
            for idx, running_line in enumerate(st.session_state.active_lines):
                if running_line == line:
                    st.session_state.active_lines.pop(idx)
            potential_interface.empty()

# Add all active lines

# Figure for plotting
fig = go.Figure()


def add_line_to_fig(line: Line):
    fig.add_trace(
        go.Scatter(
            x=line.spectrum.x,
            y=-line.spectrum.y if line.inverse else line.spectrum.y,
            mode="lines",
            name=line.spectrum.name,
            line=dict(color=line.color, width=line.width, dash=line.dash),
            opacity=line.opacity,
        )
    )


# Add all active lines to the figure
for line in all_active_lines():
    add_line_to_fig(line)

# Configure the figure layout
fig.update_layout(
    hovermode="x unified",
    dragmode="zoom",
    xaxis_rangeslider_visible=True,
)

# Display the figure in the designated plot slot at the top of the page
plot_slot.plotly_chart(fig, use_container_width=True)
