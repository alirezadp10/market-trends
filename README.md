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
git clone https://github.com/alirezadp10/market-trends.git
cd market-trends

# Install dependencies
make install
```

## Quick Start

```bash
make help        # Show all available commands
make run         # Execute the notebook
make lab         # Start Jupyter Lab
make fetch       # Fetch latest market data
```

## Make Commands

| Command | Description |
|---------|-------------|
| `make install` | Create venv and install dependencies |
| `make sync` | Sync dependencies with uv |
| `make run` | Execute the notebook |
| `make lab` | Start Jupyter Lab |
| `make notebook` | Start Jupyter Notebook |
| `make fetch` | Fetch all market data |
| `make fetch-market MARKET=Dollar` | Fetch specific market |
| `make markets` | List available markets |
| `make db-stats` | Show database statistics |
| `make lint` | Run linter (ruff) |
| `make format` | Format code (ruff) |
| `make test` | Run tests |
| `make clean` | Remove cache files |

## Usage

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

### Fetch Data Programmatically

```python
from src.data_fetcher import fetch_all_markets, fetch_market, get_available_markets

# List available markets
print(get_available_markets())

# Fetch all markets and update database
df = fetch_all_markets()

# Fetch specific markets only
df = fetch_all_markets(markets=["Dollar", "Bitcoin", "Coin"])

# Fetch single market
df = fetch_market("Dollar")
```

## Configuration

Copy `.env.example` to `.env` to customize settings:

```bash
cp .env.example .env
```

Available settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_FILE` | `market_data.db` | Database file path |
| `START_YEAR` | `1395` | Start year (Jalali) |
| `END_YEAR` | `1410` | End year (Jalali) |
| `API_TIMEOUT` | `30` | API request timeout (seconds) |
| `API_MAX_RETRIES` | `3` | Max retry attempts |
| `NFUSION_TOKEN` | - | NFusion API token for Silver |

## Project Structure

```
market-trends/
├── Makefile            # Project commands
├── market.ipynb        # Main analysis notebook
├── market_data.db      # SQLite database with historical data
├── events.csv          # Market events for annotations
├── pyproject.toml      # Project configuration
├── .env.example        # Environment variables template
├── src/
│   ├── __init__.py     # Package exports
│   ├── config.py       # Constants (market names, colors, dates)
│   ├── settings.py     # Configuration management
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
