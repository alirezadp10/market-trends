# Market Trends

Analysis of Iranian market trends including stocks, gold, currency, and cryptocurrency.

## Features

- Track and compare 17+ markets (Bourse, Gold, Dollar, Bitcoin, Coins, etc.)
- Jalali (Persian) and Gregorian date support
- Growth rate analysis (yearly, seasonal, monthly)
- Market correlation heatmaps
- Multi-year period comparisons (2, 3, 4 year periods)
- Market rankings over time
- Event annotations on charts

## Installation

Requires Python 3.10+ and [uv](https://github.com/astral-sh/uv).

```bash
# Clone the repository
git clone https://github.com/yourusername/market-trends.git
cd market-trends

# Create virtual environment and install dependencies
uv venv
uv sync
```

## Usage

### Run the Notebook

```bash
# Start Jupyter Lab
uv run jupyter lab

# Or execute notebook directly
uv run jupyter nbconvert --execute --inplace market.ipynb
```

### Use as a Library

```python
from src import (
    load_market_data,
    load_events,
    enrich_dataframe,
    plot_correlation_heatmap,
    plot_market_comparison,
    MARKET_NAMES,
)
from persiantools.jdatetime import JalaliDate

# Load and prepare data
df = load_market_data()
df = enrich_dataframe(df)
events_df = load_events()

# Plot correlation between markets
plot_correlation_heatmap(df, markets=["Dollar", "Gold", "Bitcoin", "Coin"])

# Compare market performance
plot_market_comparison(
    df,
    markets=["Dollar", "Coin", "Bitcoin"],
    date_filter=JalaliDate(1402, 1, 1),
    events_df=events_df,
)
```

### Fetch Fresh Data

```python
from src.data_fetcher import fetch_all_markets

# Update database with latest data from APIs
fetch_all_markets()
```

## Project Structure

```
market-trends/
├── market.ipynb        # Main analysis notebook
├── market_data.db      # SQLite database with historical data
├── events.csv          # Market events for annotations
├── pyproject.toml      # Project configuration
├── src/
│   ├── __init__.py     # Package exports
│   ├── config.py       # Constants (market names, colors, dates)
│   ├── data_loader.py  # Database and CSV loading
│   ├── data_fetcher.py # API fetching functions
│   ├── transformers.py # DataFrame enrichment
│   └── charts.py       # Plotting functions
```

## Supported Markets

| English Name | Persian Name |
|-------------|--------------|
| Bourse | بورس |
| Fara-Bourse | فرابورس |
| Gold | طلا |
| Dollar | دلار |
| Coin | سکه امامی |
| Nim-Coin | نیم سکه |
| Rob-Coin | ربع سکه |
| Coin-Gerami | سکه گرمی |
| Bitcoin | بیت کوین |
| Silver | نقره |
| Sandoghe-Aiar | عیار-مفید |
| Bourse-Khodro | بورس خودرو |
| Khesapa | خساپا |
| Khodro | خودرو |
| Salam | صندوق سلام |
| Energy | انرژی |
| Synergy | سینرژی |

## Data Sources

- [TSETMC](https://tsetmc.com) - Tehran Stock Exchange
- [TGJU](https://tgju.org) - Gold, currency, and cryptocurrency prices
- [NFusion Solutions](https://nfusionsolutions.com) - Silver prices

## License

MIT
