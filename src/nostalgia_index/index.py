"""Index math. Pure DataFrame in, DataFrame out; no I/O."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class NostalgiaIndex:
    """Compute and hold the nostalgia index for one or more topics.

    Parameters
    ----------
    window
        Rolling-median window in days (default 28).
    baseline_months
        Number of months at the start of the series used to define 100.
    spike_factor
        Multiple of the trailing 90-day median that counts as a "revival event".

    Examples
    --------
    >>> import pandas as pd
    >>> d = pd.date_range("2016-01-01", periods=730)
    >>> v = pd.DataFrame({"date": d, "article": "A", "views": 100})
    >>> t = pd.DataFrame({"date": d, "views": 1_000_000})
    >>> NostalgiaIndex().compute(v, t).nostalgia_index.iloc[-1]
    np.float64(100.0)
    """

    window: int = 28
    baseline_months: int = 12
    spike_factor: float = 3.0

    def compute(self, views: pd.DataFrame, totals: pd.DataFrame) -> pd.DataFrame:
        """Normalize views by project traffic, smooth, and scale to the baseline.

        Parameters
        ----------
        views
            Columns ``date``, ``article``, ``views``.
        totals
            Columns ``date``, ``views`` (project-wide totals).

        Returns
        -------
        pd.DataFrame
            Columns ``date``, ``article``, ``views``, ``total_views``,
            ``views_per_million``, ``smoothed``, ``nostalgia_index`` and
            ``raw_index`` (unsmoothed, used for revival detection).
        """
        t = totals.rename(columns={"views": "total_views"})[["date", "total_views"]]
        df = views.merge(t, on="date", how="inner").sort_values(["article", "date"])
        df["views_per_million"] = df["views"] / df["total_views"] * 1e6
        out = []
        for _, g in df.groupby("article", sort=False):
            g = g.copy()
            g["smoothed"] = (
                g["views_per_million"].rolling(self.window, min_periods=1).median()
            )
            cutoff = g["date"].min() + pd.DateOffset(months=self.baseline_months)
            base = g.loc[g["date"] < cutoff, "smoothed"].median()
            base = np.nan if not base or base <= 0 else base
            g["nostalgia_index"] = g["smoothed"] / base * 100
            g["raw_index"] = g["views_per_million"] / base * 100
            out.append(g)
        cols = [
            "date", "article", "views", "total_views", "views_per_million",
            "smoothed", "nostalgia_index", "raw_index",
        ]
        if not out:
            return pd.DataFrame(columns=cols)
        return pd.concat(out, ignore_index=True)[cols]

    def revivals(self, index_df: pd.DataFrame) -> pd.DataFrame:
        """Days where the raw index exceeds ``spike_factor`` x the trailing 90-day median.

        Parameters
        ----------
        index_df
            Output of :meth:`compute`.

        Returns
        -------
        pd.DataFrame
            Columns ``date``, ``article``, ``raw_index``, ``trailing_median``,
            ``multiple``.
        """
        out = []
        for _, g in index_df.sort_values("date").groupby("article", sort=False):
            trail = g["raw_index"].shift(1).rolling(90, min_periods=30).median()
            hit = g[g["raw_index"] > self.spike_factor * trail].copy()
            hit["trailing_median"] = trail[hit.index]
            hit["multiple"] = hit["raw_index"] / hit["trailing_median"]
            out.append(hit)
        cols = ["date", "article", "raw_index", "trailing_median", "multiple"]
        if not out:
            return pd.DataFrame(columns=cols)
        return pd.concat(out, ignore_index=True)[cols]

    def summary(self, index_df: pd.DataFrame) -> pd.DataFrame:
        """Per-topic: current index, all-time peak date, % change vs baseline, revival count.

        Parameters
        ----------
        index_df
            Output of :meth:`compute`.

        Returns
        -------
        pd.DataFrame
            Columns ``article``, ``current``, ``peak``, ``peak_date``,
            ``pct_vs_baseline``, ``revivals``.
        """
        rev = self.revivals(index_df).groupby("article").size()
        rows = []
        for art, g in index_df.sort_values("date").groupby("article", sort=False):
            g = g.dropna(subset=["nostalgia_index"])
            if g.empty:
                continue
            cur = g["nostalgia_index"].iloc[-1]
            peak_row = g.loc[g["nostalgia_index"].idxmax()]
            rows.append(
                {
                    "article": art,
                    "current": cur,
                    "peak": peak_row["nostalgia_index"],
                    "peak_date": peak_row["date"],
                    "pct_vs_baseline": cur - 100,
                    "revivals": int(rev.get(art, 0)),
                }
            )
        return pd.DataFrame(
            rows,
            columns=["article", "current", "peak", "peak_date", "pct_vs_baseline", "revivals"],
        )
