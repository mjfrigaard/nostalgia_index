import datetime as dt

import httpx
import pytest
import respx

from nostalgia_index import client

MW = "https://en.wikipedia.org/w/api.php"
S, E = dt.date(2020, 1, 1), dt.date(2020, 1, 3)


def items(n=3, v=10):
    return {"items": [{"timestamp": f"202001{d:02d}00", "views": v} for d in range(1, n + 1)]}


def redirect_ok(title="Furby"):
    return httpx.Response(200, json={"query": {"pages": {"1": {"title": title}}}})


@respx.mock
def test_fetch_views_and_user_agent():
    respx.get(MW).mock(return_value=redirect_ok())
    route = respx.get(url__startswith=client.BASE).mock(
        return_value=httpx.Response(200, json=items())
    )
    df = client.fetch_views("Furby", S, E)
    assert list(df.columns) == ["date", "article", "views"]
    assert df.views.sum() == 30
    req = route.calls.last.request
    assert "nostalgia_index" in req.headers["user-agent"]
    assert "/user/" in req.url.path


@respx.mock
def test_cache_hit_avoids_network():
    respx.get(MW).mock(return_value=redirect_ok())
    route = respx.get(url__startswith=client.BASE).mock(
        return_value=httpx.Response(200, json=items())
    )
    client.fetch_views("Furby", S, E)
    client.fetch_views("Furby", S, E)
    assert route.call_count == 1


@respx.mock
def test_404_returns_empty_with_warning():
    respx.get(MW).mock(return_value=redirect_ok("Nope"))
    respx.get(url__startswith=client.BASE).mock(return_value=httpx.Response(404))
    with pytest.warns(UserWarning):
        df = client.fetch_views("Nope", S, E)
    assert df.empty


@respx.mock
def test_retry_on_429():
    respx.get(MW).mock(return_value=redirect_ok())
    route = respx.get(url__startswith=client.BASE).mock(
        side_effect=[httpx.Response(429), httpx.Response(200, json=items())]
    )
    assert len(client.fetch_views("Furby", S, E)) == 3
    assert route.call_count == 2


@respx.mock
def test_redirect_resolution():
    respx.get(MW).mock(return_value=redirect_ok("Tamagotchi"))
    route = respx.get(url__startswith=client.BASE).mock(
        return_value=httpx.Response(200, json=items())
    )
    df = client.fetch_views("Tamagochi", S, E)
    assert "Tamagotchi" in str(route.calls.last.request.url)
    assert df.article.iloc[0] == "Tamagotchi"


@respx.mock
def test_project_total():
    respx.get(url__startswith=client.BASE).mock(
        return_value=httpx.Response(200, json=items(v=1_000_000))
    )
    df = client.fetch_project_total(start=S, end=E)
    assert list(df.columns) == ["date", "views"]
    assert len(df) == 3
