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

## Starter topics

The topic dropdown starts with 92 articles in 8 categories. Michael Jordan and Nintendo 64 are selected by default, and each category has a preset button that selects its whole group.

| Category | Count | Topics |
| --- | --- | --- |
| Sports | 17 | Michael Jordan, Chicago Bulls, Space Jam, Shaquille O'Neal, Ken Griffey Jr., Sammy Sosa, Mark McGwire, Derek Jeter, Brett Favre, Dale Earnhardt, Tiger Woods, Mike Tyson, Attitude Era, WCW Monday Nitro, 1996 Summer Olympics, 1992 United States men's Olympic basketball team, Topps |
| Games | 21 | Oregon Trail II, Super Mario Bros., Nintendo 64, GoldenEye 007, Mario Kart 64, Super Smash Bros., Sega Genesis, Game Boy, Game Boy Color, PlayStation (console), Pokémon Red, Blue, and Yellow, Mortal Kombat, Street Fighter II, NBA Jam, Madden NFL, Tony Hawk's Pro Skater, Halo: Combat Evolved, Counter-Strike, StarCraft, RuneScape, Xbox network |
| TV | 13 | Dawson's Creek, Glee (TV series), One Tree Hill (TV series), Gossip Girl, Dragon Ball Z, Toonami, Cartoon Network, Nickelodeon, Teenage Mutant Ninja Turtles, Mighty Morphin Power Rangers, Cowboy Bebop, Beavis and Butt-Head, Jackass (franchise) |
| Music | 15 | Taylor Swift, Beyoncé, Backstreet Boys, Michael Jackson, Eminem, Weezer, The Pussycat Dolls, Alanis Morissette, Britney Spears, The Eras Tour, Blink-182, Linkin Park, Limp Bizkit, Green Day, Wu-Tang Clan |
| Films | 6 | Mean Girls, Barbie (film), Star Wars, The Matrix, Fight Club, American Pie (film) |
| Books | 3 | Harry Potter, Twilight (novel series), The Hunger Games |
| Toys | 8 | Lego, Nerf, Hot Wheels, Transformers, Beyblade, Magic: The Gathering, Yu-Gi-Oh!, Milk caps (game) |
| Tech | 9 | Instant camera, Phonograph record, Blockbuster (retailer), Napster, LimeWire, AIM (software), Myspace, Mountain Dew, Jolt Cola |

## Building the documentation

The documentation site is built with `great-docs`, which needs the dev extras and [Quarto](https://quarto.org/docs/get-started/) installed. The first command below builds the site, and the second opens it in a browser.

```bash
great-docs build      # build the site into great-docs/_site
great-docs preview    # open it in your browser
```

Site settings live in `great-docs.yml`, and the guide pages live in `user_guide/*.qmd`. Reserve `great-docs init --force` for resetting the configuration.
