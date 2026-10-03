"""Wikimedia REST client with a User-Agent, retries and an on-disk cache."""

from __future__ import annotations

import datetime as dt
import os
import time
import urllib.parse
import warnings

import httpx
import pandas as pd
from diskcache import Cache

BASE = "https://wikimedia.org/api/rest_v1/metrics/pageviews"
MEDIAWIKI = "https://{lang}.wikipedia.org/w/api.php"
USER_AGENT = (
    "nostalgia_index/0.1 (https://github.com/you/nostalgia_index; you@example.com)"
)
DATA_FLOOR = dt.date(2015, 7, 1)
_RETRY_STATUS = {429, 500, 502, 503, 504}
_cache: Cache | None = None


def _get_cache() -> Cache:
    global _cache
    if _cache is None:
        path = os.environ.get("NOSTALGIA_CACHE_DIR", "~/.cache/nostalgia_index")
        _cache = Cache(os.path.expanduser(path))
    return _cache


def _client() -> httpx.Client:
    return httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=30)


def _get_json(url: str, params: dict | None = None, retries: int = 4) -> dict | None:
    """GET JSON, retrying 429/5xx with exponential backoff. Returns None on 404."""
    with _client() as c:
        for attempt in range(retries + 1):
            r = c.get(url, params=params)
            if r.status_code == 404:
                return None
            if r.status_code in _RETRY_STATUS and attempt < retries:
                time.sleep(min(2**attempt, 30) * 0.5)
                continue
            r.raise_for_status()
            return r.json()
    return None


def _stamp(d: dt.date) -> str:
    return d.strftime("%Y%m%d") + "00"


def _frame(items: list[dict], article: str | None, key: str) -> pd.DataFrame:
    rows = [
        {
            "date": pd.to_datetime(i["timestamp"][:8], format="%Y%m%d"),
            "article": article,
            "views": i[key],
        }
        for i in items
    ]
    df = pd.DataFrame(rows, columns=["date", "article", "views"])
    return df if article is not None else df.drop(columns="article")


def resolve_title(article: str, project: str = "en.wikipedia") -> str | None:
    """Resolve redirects via the MediaWiki API (``"Tamagochi"`` to ``"Tamagotchi"``).

    Parameters
    ----------
    article
        Article title as typed by a user.
    project
        Wikimedia project, e.g. ``"en.wikipedia"``.

    Returns
    -------
    str or None
        Canonical title with underscores, or ``None`` if the page is missing.
    """
    lang = project.split(".")[0]
    params = {
        "action": "query",
        "titles": article.replace("_", " "),
        "redirects": 1,
        "format": "json",
    }
    data = _get_json(MEDIAWIKI.format(lang=lang), params)
    if not data:
        return None
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        if "missing" in page or "invalid" in page:
            return None
        return page["title"].replace(" ", "_")
    return None


def fetch_views(
    article: str,
    start: dt.date = DATA_FLOOR,
    end: dt.date | None = None,
    project: str = "en.wikipedia",
    granularity: str = "daily",
) -> pd.DataFrame:
    """Fetch daily pageviews for a single Wikipedia article.

    Parameters
    ----------
    article
        Article title, e.g. ``"Tamagotchi"``. Spaces are converted to
        underscores and the title is URL-encoded for you. Redirects are
        resolved first.
    start, end
        Inclusive date range. Data is available from 2015-07-01.
    project
        Wikimedia project, e.g. ``"en.wikipedia"``.
    granularity
        ``"daily"`` or ``"monthly"``.

    Returns
    -------
    pd.DataFrame
        Columns ``date``, ``article``, ``views``. Empty (with a warning) if
        the article has no data for the range.

    Examples
    --------
    >>> df = fetch_views("Furby", start=dt.date(2020, 1, 1), end=dt.date(2020, 12, 31))  # doctest: +SKIP
    >>> df.views.sum() > 0  # doctest: +SKIP
    True
    """
    end = end or dt.date.today() - dt.timedelta(days=1)
    start = max(start, DATA_FLOOR)
    key = (article, project, str(start), str(end), granularity)
    cache = _get_cache()
    if key in cache:
        return cache[key].copy()

    title = resolve_title(article, project) or article.replace(" ", "_")
    url = "/".join(
        [
            BASE,
            "per-article",
            project,
            "all-access",
            "user",
            urllib.parse.quote(title, safe=""),
            granularity,
            _stamp(start),
            _stamp(end),
        ]
    )
    data = _get_json(url)
    if data is None:
        warnings.warn(f"No pageview data for {article!r} ({start} to {end}).")
        return pd.DataFrame(columns=["date", "article", "views"])
    df = _frame(data["items"], title.replace("_", " "), "views")
    cache[key] = df
    return df.copy()


def fetch_project_total(
    project: str = "en.wikipedia",
    start: dt.date = DATA_FLOOR,
    end: dt.date | None = None,
    granularity: str = "daily",
    **kw,
) -> pd.DataFrame:
    """Fetch total daily views for a project (``/aggregate/`` endpoint), used as the denominator.

    Parameters
    ----------
    project
        Wikimedia project, e.g. ``"en.wikipedia"``.
    start, end
        Inclusive date range.
    granularity
        ``"daily"`` or ``"monthly"``.

    Returns
    -------
    pd.DataFrame
        Columns ``date``, ``views``.
    """
    end = end or dt.date.today() - dt.timedelta(days=1)
    start = max(start, DATA_FLOOR)
    key = ("__total__", project, str(start), str(end), granularity)
    cache = _get_cache()
    if key in cache:
        return cache[key].copy()
    url = "/".join(
        [
            BASE,
            "aggregate",
            project,
            "all-access",
            "user",
            granularity,
            _stamp(start),
            _stamp(end),
        ]
    )
    data = _get_json(url)
    if data is None:
        warnings.warn(f"No project totals for {project} ({start} to {end}).")
        return pd.DataFrame(columns=["date", "views"])
    df = _frame(data["items"], None, "views")
    cache[key] = df
    return df.copy()
