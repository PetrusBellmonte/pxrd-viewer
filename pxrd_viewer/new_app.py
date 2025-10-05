from menutheme import register_nav_page, menutheme
from nicegui import ui, app, binding
import plotly.graph_objects as go
from data_sources import list_available_spectra, Spectrum
from dataclasses import dataclass
import altui

import pages.new_add_spectrum
import pages.new_edit_spectra


@binding.bindable_dataclass
class Line:
    spectrum: Spectrum
    color: str
    opacity: float
    dash: str
    width: float
    title: str = None
    can_be_deleted: bool = True
    inverse: bool = True
    _display_name: str = None

    @property
    def display_name(self):
        if self._display_name is None:
            return self.spectrum.readable_name
        return self._display_name
    @display_name.setter
    def display_name(self, value):
        self._display_name = value

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
        assert spectrum is not None, "Spectrum must be provided."
        return cls(
            spectrum=spectrum,
            color=color,
            opacity=opacity,
            dash=dash,
            width=width,
            **kwargs,
        )
    def controller(self):
        with ui.expansion().bind_text_from(self,'display_name',lambda x: self.title if self.title else x) as expansion:
            ui.input('Display name', value=self.display_name, on_change=update_figure).bind_value(self,'display_name')
            def update_line_color(e):
                self.color = e.color
                update_figure()
            with ui.button(icon='palette'):
                picker = ui.color_picker(on_pick=update_line_color)
                picker.q_color.props('default-view=palette no-header')
            altui.slider(0.01, 1.0, label='Opacity', display_value=True, step=0.01, on_change=update_figure).bind_value(self, 'opacity')
            ui.select(["solid", "dot", "dash", "longdash", "dashdot", "longdashdot"], label='Line style', value=self.dash, on_change=update_figure).bind_value(self, 'dash')
            altui.slider(0, 3, step=0.1, label='Width', display_value=True, on_change=update_figure).bind_value(self, 'width')
            ui.checkbox('Invert spectrum', on_change=update_figure).bind_value(self, 'inverse')
            def delete_line():
                app.storage.client['active_lines'].remove(self)
                expansion.delete()
                update_figure()
            ui.button('Delete', on_click=delete_line).bind_visibility_from(self, 'can_be_deleted')
        return expansion

def next_spectrum(spectrum: Spectrum | None = None) -> Spectrum:
    """
    Get the next fitting spectrum in the list, or the first one if None is given.

    @param spectrum: The current spectrum to find the next of.
    @return: The next spectrum in the list, or the first one if None is given.
    """
    spectra = app.storage.client.get('spectra', [])
    assert len(spectra) > 0, "No spectra available."
    if spectrum is None:
        return spectra[0]
    for i, s in enumerate(spectra):
        if s == spectrum:
            return spectra[(i + 1) % len(spectra)]
    else:
        raise ValueError("Given spectrum is not in the list of available spectra.")


def all_active_lines():
    selected_line = app.storage.client.get('selected_line', None)
    if selected_line:
        yield selected_line
    rotation_line = app.storage.client.get('rotation_line', None)
    if rotation_line:
        yield rotation_line
    yield from app.storage.client.get('active_lines', [])

def update_figure(*args, **kwargs):
    fig = app.storage.client['fig']
    fig.data = tuple()
    for line in all_active_lines():
        fig.add_trace(
            go.Scatter(
                x=line.spectrum.x,
                y=-line.spectrum.y if line.inverse else line.spectrum.y,
                mode="lines",
                name=line.display_name,
                line=dict(color=line.color, width=line.width, dash=line.dash),
                opacity=line.opacity,
            )
        )
    fig.update_layout(uirevision='constant')
    app.storage.client['plot'].update()

def on_select_spectrum(e):
    selected_obj = next(s for s in app.storage.client['spectra'] if s.name == e.value)
    app.storage.client['selected_line'].spectrum = selected_obj
    update_figure()

def add_line_controller(line: Line, move_to_top: bool = False):
    line_controls = app.storage.client.get('line_controls', None)
    if line_controls:
        with line_controls:
            element = line.controller()
            app.storage.client['line_controllers'][id(line)] = element
            if move_to_top:
                element.move(target_index=2) # todo: make dynamic based on number of static elements
    update_figure()

@register_nav_page("/", display_name="Spectrum Viewer", favicon="📈")
def main():
    with menutheme("Spectrum Viewer"):
        spectra = list_available_spectra()
        app.storage.client['spectra'] = spectra
        spectrum_names = [s.name for s in spectra]
        
        app.storage.client['active_lines'] = []

        if not spectra:
            ui.label("No spectra available. Please add spectra first.").classes('text-red')
        else:
            selected_obj = spectra[0]
            selected_line = Line.from_spectrum(
                selected_obj,
                color="#FF0000",
                can_be_deleted=False,
                title="(Selected)",
                inverse=False,
            )
            app.storage.client['selected_line'] = selected_line

            fig = go.Figure()
            fig.update_layout(
                hovermode="x unified",
                dragmode="zoom",
                xaxis_rangeslider_visible=True,
                margin_t=20,
                margin_b=20,
                margin_l=20,
            )
            app.storage.client['fig'] = fig

            plot = ui.plotly(fig).style('height: 450px;').classes('w-full h-full')
            app.storage.client['plot'] = plot
            
            update_figure()

            # Controls
            ui.select(spectrum_names, label='Select a spectrum to view', value=spectrum_names[0], on_change=on_select_spectrum).classes('w-1/2')

            # Rotation interface
            def next_spectrum(spectrum=None):
                if not spectra:
                    return None
                if spectrum is None:
                    return spectra[0]
                for i, s in enumerate(spectra):
                    if s == spectrum:
                        return spectra[(i + 1) % len(spectra)]
                return spectra[0]

            # Rotation
            app.storage.client['rotation_line'] = None
            with ui.row().classes('items-center') as rotation_controls:
                def activate_rotation():
                    selected_spectrum = next_spectrum()
                    rot_line = Line.from_spectrum(selected_spectrum, can_be_deleted=False, title='(Rot)')
                    app.storage.client['rotation_line'] =  rot_line
                    add_line_controller(rot_line,move_to_top=True)
                    update_figure()

                def delete_rotation():
                    line = app.storage.client.get('rotation_line', None)
                    if line:
                        app.storage.client['line_controllers'][id(line)].delete()
                    app.storage.client['rotation_line'] = None
                    update_figure()

                def pin_rotation():
                    rot_line = app.storage.client.get('rotation_line', None)
                    if rot_line:
                        rot_line.can_be_deleted = True
                        rot_line.title = None
                        app.storage.client['active_lines'].append(rot_line)
                        app.storage.client['rotation_line'] = None
                        update_figure()

                def next_rotation():
                    rot_line = app.storage.client.get('rotation_line', None)
                    if rot_line:
                        rot_line.spectrum = next_spectrum(rot_line.spectrum)
                        selected_spectrum = rot_line.spectrum
                        update_figure()
                def set_selected_spectrum(e):
                    rot_line = app.storage.client.get('rotation_line', None)
                    if rot_line:
                        selected_obj = next(s for s in spectra if s.name == e.value)
                        rot_line.spectrum = selected_obj
                        update_figure()

                ui.button('Activate Spectrum Rotation', on_click=activate_rotation).bind_visibility_from(app.storage.client, 'rotation_line', lambda x: x is None)
                with ui.row().classes('items-center').bind_visibility_from(app.storage.client, 'rotation_line', lambda x: x is not None):
                    ui.select(spectrum_names, label='Rotating Spectrum', on_change=set_selected_spectrum).bind_value_from(app.storage.client, 'rotation_line', backward=lambda x: x.spectrum.name if x else None).classes('w-1/4')
                    ui.button('Delete', on_click=delete_rotation)
                    ui.button('Next', on_click=next_rotation)
                    ui.button('Pin', on_click=pin_rotation)

            app.storage.client['line_controllers'] = {}
            with ui.column().classes('w-full') as line_controls:
                ui.label('Spectra in View').classes('text-lg font-semibold mt-4')
                for line in all_active_lines():
                    element = line.controller()
                    app.storage.client['line_controllers'][id(line)] = element
                app.storage.client['line_controls'] = line_controls

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="PXRD Viewer",favicon="📈",reload=False)