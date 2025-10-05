from typing import Callable
from nicegui import ui


def tag_select(options, label, **kwargs):
    element = (
        ui.select(
            options=options, with_input=True, multiple=True, label=label, **kwargs
        )
        .props("new-value-mode=add-unique use-chips")
        .classes("my-chips")
    )
    ui.add_head_html(
        "<style>.my-chips .q-chip {font-size: 1rem; padding: 0.5em 0.5em; border-radius: 12px;}</style>"  # noqa: E501
    )
    # use add_slot on selected-item but how to get value??
    return element


def slider(
    min,
    max,
    display_value: bool | Callable[[float], str] = None,
    label: str = None,
    **kwargs,
):
    if label is not None:
        ui.label(label)
    if display_value is None:
        return ui.slider(min=min, max=max, **kwargs)
    if display_value is True:
        display_value = lambda x: str(x)
    s = ui.slider(min=min, max=max, **kwargs).props("label-always")
    s.bind_value_to(s.props, "label-value", display_value)
    return s
