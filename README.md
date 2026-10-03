# nostalgia_index

Wikipedia pageviews as a cultural pulse. Normalizes article views by total Wikipedia traffic, smooths with a rolling median, and scales to a 2015 baseline of 100.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -e ".[dev]"        # from a clone; or: pip install nostalgia_index
```

Deactivate with `deactivate`.

## Usage

```bash
nostalgia fetch Tamagotchi Furby --out index.csv
nostalgia run
```

```python
import datetime as dt
from nostalgia_index import fetch_views, fetch_project_total, NostalgiaIndex

views = fetch_views("Furby")
totals = fetch_project_total()
idx = NostalgiaIndex().compute(views, totals)
```

## Docs

Requires the dev extras and [Quarto](https://quarto.org/docs/get-started/).

```bash
great-docs build      # build the site into great-docs/_site
great-docs preview    # open it in your browser
```

Edit `great-docs.yml` for site settings and `user_guide/*.qmd` for guide pages. Run `great-docs init --force` only to reset the config.
