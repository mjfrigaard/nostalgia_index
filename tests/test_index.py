import numpy as np
import pandas as pd

from nostalgia_index import NostalgiaIndex


def series(values, article="A", start="2016-01-01"):
    d = pd.date_range(start, periods=len(values))
    v = pd.DataFrame({"date": d, "article": article, "views": values})
    t = pd.DataFrame({"date": d, "views": 1_000_000})
    return v, t


def test_flat_series_is_100():
    v, t = series([100] * 730)
    out = NostalgiaIndex().compute(v, t)
    assert np.allclose(out.nostalgia_index, 100)


def test_doubling_after_baseline_is_200():
    v, t = series([100] * 400 + [200] * 400)
    out = NostalgiaIndex().compute(v, t)
    assert out.nostalgia_index.iloc[-1] == 200


def test_traffic_drift_is_controlled():
    d = pd.date_range("2016-01-01", periods=800)
    v = pd.DataFrame({"date": d, "article": "A", "views": np.where(np.arange(800) < 400, 100, 200)})
    t = pd.DataFrame({"date": d, "views": np.where(np.arange(800) < 400, 1e6, 2e6)})
    assert np.isclose(NostalgiaIndex().compute(v, t).nostalgia_index.iloc[-1], 100)


def test_revival_detected_and_smoothed_away():
    vals = [100] * 600
    vals[500] = 1000
    v, t = series(vals)
    ni = NostalgiaIndex()
    out = ni.compute(v, t)
    rev = ni.revivals(out)
    assert list(rev.date) == [out.date[500]]
    assert out.nostalgia_index.max() == 100


def test_summary():
    v, t = series([100] * 400 + [200] * 400)
    ni = NostalgiaIndex()
    s = ni.summary(ni.compute(v, t))
    assert s.current.iloc[0] == 200
    assert s.pct_vs_baseline.iloc[0] == 100
    assert s.revivals.iloc[0] == 0


def test_multiple_topics_independent():
    a, t = series([100] * 500, "A")
    b, _ = series([5] * 500, "B")
    out = NostalgiaIndex().compute(pd.concat([a, b]), t)
    assert np.allclose(out.nostalgia_index, 100)
