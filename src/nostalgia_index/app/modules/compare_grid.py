import plotly.express as px
from shiny import module, reactive, render, ui
from shinywidgets import output_widget, render_plotly

from ...index import NostalgiaIndex
from ..theme import COLORWAY


@module.ui
def grid_ui():
    return ui.TagList(
        ui.card(ui.card_header("Small multiples"), output_widget("facets"), full_screen=True),
        ui.card(
            ui.card_header("Summary", ui.download_button("download", "CSV", class_="btn-sm float-end")),
            ui.output_data_frame("summary"),
        ),
    )


@module.server
def grid_server(input, output, session, index_df: reactive.Calc):
    @reactive.calc
    def summ():
        return NostalgiaIndex().summary(index_df())

    @render_plotly
    def facets():
        fig = px.line(
            index_df(), x="date", y="nostalgia_index", facet_col="article",
            facet_col_wrap=3, color="article", color_discrete_sequence=COLORWAY,
        )
        fig.update_layout(showlegend=False)
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        return fig

    @render.data_frame
    def summary():
        return render.DataGrid(summ().round(1))

    @render.download(filename="nostalgia-summary.csv")
    def download():
        yield summ().to_csv(index=False)
