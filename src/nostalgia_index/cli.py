"""Command line interface."""

from __future__ import annotations

import datetime as dt

import click
import pandas as pd

from .client import fetch_project_total, fetch_views
from .index import NostalgiaIndex


@click.group()
def cli():
    """Nostalgia Index: Wikipedia pageviews as a cultural pulse."""


@cli.command()
@click.argument("topics", nargs=-1, required=True)
@click.option("--out", type=click.Path(), default="index.csv", help="Output CSV path.")
@click.option("--window", default=28, show_default=True, help="Rolling median days.")
def fetch(topics, out, window):
    """Compute the index for TOPICS and write a CSV."""
    start, end = dt.date(2015, 7, 1), dt.date.today() - dt.timedelta(days=1)
    frames = [fetch_views(t, start, end) for t in topics]
    views = pd.concat([f for f in frames if not f.empty], ignore_index=True)
    if views.empty:
        raise click.ClickException("No data found for the given topics.")
    totals = fetch_project_total(start=start, end=end)
    NostalgiaIndex(window=window).compute(views, totals).to_csv(out, index=False)
    click.echo(f"Wrote {out}")


@cli.command()
@click.option("--port", default=8000, show_default=True, help="Port to serve on.")
def run(port):
    """Launch the Shiny app."""
    from .app import run_app

    run_app(port=port)
