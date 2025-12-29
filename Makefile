.PHONY: help install sync run lab fetch fetch-market clean lint test

# Default target
help:
	@echo "Market Trends - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install     - Create venv and install dependencies"
	@echo "  make sync        - Sync dependencies with uv"
	@echo ""
	@echo "Run:"
	@echo "  make run         - Execute the notebook"
	@echo "  make lab         - Start Jupyter Lab"
	@echo "  make notebook    - Start Jupyter Notebook"
	@echo ""
	@echo "Data:"
	@echo "  make fetch       - Fetch all market data"
	@echo "  make fetch-market MARKET=Dollar  - Fetch specific market"
	@echo "  make markets     - List available markets"
	@echo ""
	@echo "Development:"
	@echo "  make lint        - Run linter (ruff)"
	@echo "  make format      - Format code (ruff)"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Remove cache files"
	@echo ""

# Setup
install:
	~/.local/bin/uv venv
	~/.local/bin/uv sync

sync:
	~/.local/bin/uv sync

# Run
run:
	~/.local/bin/uv run jupyter nbconvert --to notebook --execute --inplace market.ipynb

lab:
	~/.local/bin/uv run jupyter lab

notebook:
	~/.local/bin/uv run jupyter notebook

# Data fetching
fetch:
	~/.local/bin/uv run python3 -c "from src.data_fetcher import fetch_all_markets; fetch_all_markets()"

fetch-market:
ifndef MARKET
	$(error MARKET is not set. Usage: make fetch-market MARKET=Dollar)
endif
	~/.local/bin/uv run python3 -c "from src.data_fetcher import fetch_market, update_database; df = fetch_market('$(MARKET)'); update_database(df) if not df.empty else None"

markets:
	@~/.local/bin/uv run python3 -c "from src.data_fetcher import get_available_markets; print('\n'.join(get_available_markets()))"

# Development
lint:
	~/.local/bin/uv run ruff check src/

format:
	~/.local/bin/uv run ruff format src/

test:
	~/.local/bin/uv run pytest tests/ -v

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true

# Database
db-shell:
	sqlite3 market_data.db

db-stats:
	@~/.local/bin/uv run python3 -c "from src import load_market_data; df = load_market_data(); print(f'Total records: {len(df)}'); print(df.groupby('market_type').size())"
