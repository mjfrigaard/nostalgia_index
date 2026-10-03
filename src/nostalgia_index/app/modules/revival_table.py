import urllib.parse

import pandas as pd
from great_tables import GT
from shiny import module, reactive, render, ui

from ...index import NostalgiaIndex


def _links(row) -> str:
    title = urllib.parse.quote(row["article"].replace(" ", "_"))
    day = row["date"].strftime("%Y%m%d")
    wiki = f"https://en.wikipedia.org/wiki/{title}"
    way = f"https://web.archive.org/web/{day}/{wiki}"
    return f"[Article]({wiki}) · [Wayback]({way})"


@module.ui
def table_ui():
    return ui.card(
        ui.card_header("Revival events"),
        ui.output_ui("table"),
        full_screen=True,
    )


@module.server
def table_server(input, output, session, index_df: reactive.Calc, spike_factor=None):
    @render.ui
    def table():
        sf = spike_factor() if spike_factor else 3.0
        rev = NostalgiaIndex(spike_factor=sf).revivals(index_df())
        if rev.empty:
            return ui.p("No revival events found.")
        rev = rev.sort_values("multiple", ascending=False).copy()
        rev["links"] = rev.apply(_links, axis=1)
        rev["date"] = pd.to_datetime(rev["date"]).dt.strftime("%Y-%m-%d")
        gt = (
            GT(rev[["date", "article", "raw_index", "multiple", "links"]])
            .fmt_number(["raw_index"], decimals=0)
            .fmt_number(["multiple"], decimals=1)
            .fmt_markdown("links")
            .cols_label(
                date="Date", article="Topic", raw_index="Index",
                multiple="x trailing median", links="Links",
            )
        )
        return ui.HTML(gt.as_raw_html())
