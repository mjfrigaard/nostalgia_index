# nostalgia_index

Which childhood toys, games, and athletes are people still looking up? `nostalgia_index` answers that question with Wikipedia pageviews. Raw view counts are hard to compare, because overall Wikipedia traffic has drifted since 2015 and some articles are simply more popular than others. The package normalizes each article's views by total Wikipedia traffic, smooths them with a rolling median, and scales the result so the article's first 12 months of data equal 100.

## Setup

The commands below create a virtual environment, activate it, and install the package with its development extras.

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -e ".[dev]"        # from a clone; or: pip install nostalgia_index
```

When you're finished, run `deactivate` to leave the virtual environment.

## Usage

The command line interface covers the two most common tasks. `nostalgia fetch` computes the index for one or more articles and writes it to a CSV, and `nostalgia run` launches the Shiny app.

```bash
nostalgia fetch Tamagotchi Furby --out index.csv
nostalgia run
```

From Python, the same pipeline takes three calls: fetch an article's daily views, fetch the project totals, and pass both to `NostalgiaIndex().compute()`.

```python
import datetime as dt
from nostalgia_index import fetch_views, fetch_project_total, NostalgiaIndex

views = fetch_views("Furby")
totals = fetch_project_total()
idx = NostalgiaIndex().compute(views, totals)
```

## Building the documentation

The documentation site is built with `great-docs`, which needs the dev extras and [Quarto](https://quarto.org/docs/get-started/) installed. The first command below builds the site, and the second opens it in a browser.

```bash
great-docs build      # build the site into great-docs/_site
great-docs preview    # open it in your browser
```

Site settings live in `great-docs.yml`, and the guide pages live in `user_guide/*.qmd`. Reserve `great-docs init --force` for resetting the configuration.
