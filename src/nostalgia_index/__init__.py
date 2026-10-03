"""Nostalgia Index: Wikipedia pageviews as a cultural pulse."""

from .client import fetch_project_total, fetch_views
from .index import NostalgiaIndex


def run_app(port: int = 8000, launch_browser: bool = True) -> None:
    """Launch the Nostalgia Index Shiny app.

    Parameters
    ----------
    port
        Port to serve on.
    launch_browser
        Open a browser tab on start.
    """
    from .app import run_app as _run

    _run(port=port, launch_browser=launch_browser)


__all__ = ["fetch_views", "fetch_project_total", "NostalgiaIndex", "run_app"]
