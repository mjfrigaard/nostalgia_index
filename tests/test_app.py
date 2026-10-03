import pytest
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

pytest.importorskip("playwright")
from playwright.sync_api import Page, expect  # noqa: E402

app = create_app_fixture("app_entry.py")


def test_app_loads(page: Page, app: ShinyAppProc):
    page.goto(app.url)
    expect(page.get_by_text("Nostalgia Index").first).to_be_visible()
    expect(page.get_by_role("button", name="Compute index")).to_be_visible()
