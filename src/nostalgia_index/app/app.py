from pathlib import Path

import pandas as pd
from shiny import App, reactive, render, req, ui

from ..client import fetch_project_total, fetch_views
from ..index import NostalgiaIndex
from .modules import compare_grid, index_chart, revival_table, topic_picker

METHODOLOGY_MD = """
Raw pageviews drift with overall Wikipedia traffic and differ wildly in scale, so the index normalizes twice.

1. views per million = article views / total project views x 1e6
2. smoothed = rolling median (default 28 days)
3. index = smoothed / baseline median x 100, baseline = first 12 months

An index above 100 means a topic is more talked about than in its baseline period.
A revival event is a day where the index exceeds 3x its trailing 90 day median.
Data: Wikimedia REST API, `agent=user` (spiders excluded), from July 2015.
Topics without an article in 2015 have no true baseline.
"""

app_ui = ui.page_sidebar(
    ui.sidebar(
        topic_picker.picker_ui("picker"),
        ui.input_slider("window", "Smoothing (days)", 7, 90, 28),
        ui.input_date_range("dates", "Date range", start="2015-07-01"),
        ui.input_action_button("go", "Compute index", class_="btn-primary"),
        width=320,
    ),
    ui.layout_columns(
        ui.value_box("Peak topic", ui.output_text("peak_topic")),
        ui.value_box("Biggest comeback", ui.output_text("comeback")),
        ui.value_box("Revival events", ui.output_text("n_revivals")),
        fill=False,
    ),
    ui.navset_card_tab(
        ui.nav_panel("Index over time", index_chart.chart_ui("chart")),
        ui.nav_panel("Revival events", revival_table.table_ui("revivals")),
        ui.nav_panel("Compare", compare_grid.grid_ui("grid")),
        ui.nav_panel("Methodology", ui.markdown(METHODOLOGY_MD)),
    ),
    ui.include_css(Path(__file__).parent / "www" / "custom.css"),
    ui.input_dark_mode(mode="dark"),
    title="📼 Nostalgia Index",
)


def server(input, output, session):
    topics = topic_picker.picker_server("picker")

    @reactive.calc
    @reactive.event(input.go)
    def index_df():
        req(topics())
        start, end = input.dates()
        with ui.Progress(min=0, max=len(topics())) as p:
            frames = []
            for i, t in enumerate(topics()):
                p.set(i, message=f"Fetching {t}…")
                frames.append(fetch_views(t, start, end))
        frames = [f for f in frames if not f.empty]
        req(frames)
        totals = fetch_project_total(start=start, end=end)
        return NostalgiaIndex(window=input.window()).compute(
            pd.concat(frames, ignore_index=True), totals
        )

    @reactive.calc
    def summ():
        return NostalgiaIndex(window=input.window()).summary(index_df())

    index_chart.chart_server("chart", index_df)
    revival_table.table_server("revivals", index_df)
    compare_grid.grid_server("grid", index_df)

    @render.text
    def peak_topic():
        s = summ()
        return s.loc[s["peak"].idxmax(), "article"]

    @render.text
    def comeback():
        s = summ()
        return s.loc[s["pct_vs_baseline"].idxmax(), "article"]

    @render.text
    def n_revivals():
        return str(int(summ()["revivals"].sum()))


app = App(app_ui, server, static_assets=Path(__file__).parent / "www")
