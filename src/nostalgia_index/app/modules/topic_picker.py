from shiny import module, reactive, req, ui

from ...client import resolve_title
from ...topics import PRESETS

_ALL = sorted({t for v in PRESETS.values() for t in v})


@module.ui
def picker_ui():
    return ui.TagList(
        ui.input_selectize(
            "topics", "Topics", _ALL, selected=["Michael Jordan", "Nintendo 64"], multiple=True
        ),
        ui.div(
            *[
                ui.input_action_button(f"preset_{k}", k, class_="btn-sm btn-outline-secondary")
                for k in PRESETS
            ],
            class_="d-flex flex-wrap gap-1 mb-2",
        ),
        ui.input_text("custom", "Add an article", placeholder="e.g. Tamagochi"),
        ui.input_action_button("add", "Add", class_="btn-sm"),
    )


@module.server
def picker_server(input, output, session):
    extra: reactive.Value[list[str]] = reactive.Value([])

    def _make_preset(name):
        @reactive.effect
        @reactive.event(input[f"preset_{name}"])
        def _():
            ui.update_selectize("topics", selected=PRESETS[name])

    for name in PRESETS:
        _make_preset(name)

    @reactive.effect
    @reactive.event(input.add)
    def _add():
        text = input.custom().strip()
        req(text)
        title = resolve_title(text)
        if title is None:
            ui.notification_show(f"No Wikipedia article for {text!r}", type="warning")
            return
        title = title.replace("_", " ")
        extra.set(list(dict.fromkeys([*extra(), title])))
        ui.update_selectize(
            "topics",
            choices=sorted({*_ALL, *extra()}),
            selected=[*input.topics(), title],
        )
        ui.update_text("custom", value="")

    @reactive.calc
    def selected() -> list[str]:
        return list(input.topics())

    return selected
