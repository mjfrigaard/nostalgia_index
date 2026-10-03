import pytest


@pytest.fixture(autouse=True)
def _tmp_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("NOSTALGIA_CACHE_DIR", str(tmp_path / "cache"))
    import nostalgia_index.client as c

    monkeypatch.setattr(c, "_cache", None)
    monkeypatch.setattr(c.time, "sleep", lambda s: None)
