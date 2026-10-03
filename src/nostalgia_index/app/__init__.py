"""Shiny Core app."""


def run_app(port: int = 8000, launch_browser: bool = True) -> None:
    """Launch the Nostalgia Index Shiny app."""
    from shiny import run_app as _run

    _run("nostalgia_index.app.app:app", port=port, launch_browser=launch_browser)
