import plotly.express as px
from shiny import module, reactive, ui

from ..theme import COLORWAY, PLOTLY_LAYOUT
from shinywidgets import output_widget, render_plotly


@module.ui
def chart_ui():
    return ui.card(
        ui.card_header("Nostalgia index (baseline = 100)"),
        ui.input_switch("log_y", "Log scale", False),
        output_widget("plot"),
        full_screen=True,
    )


@module.server
def chart_server(input, output, session, index_df: reactive.Calc):
    @render_plotly
    def plot():
        df = index_df()
        fig = px.line(df, x="date", y="nostalgia_index", color="article", color_discrete_sequence=COLORWAY)
        fig.add_hline(y=100, line_dash="dot", annotation_text="baseline")
        if input.log_y():
            fig.update_yaxes(type="log")
        fig.update_layout(**PLOTLY_LAYOUT)
        return fig
