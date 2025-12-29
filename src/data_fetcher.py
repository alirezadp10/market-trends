"""
Data fetching module for retrieving market data from various APIs.

Supports:
- TSETMC API (Tehran Stock Exchange)
- TGJU API (Gold, Dollar, Coins, etc.)
- NFusion Solutions API (Silver)
"""

from __future__ import annotations

import logging
import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

import pandas as pd
import requests
from persiantools.jdatetime import JalaliDate

from .config import DB_FILE
from .data_loader import get_db_connection

logger = logging.getLogger(__name__)


class MarketSource(Enum):
    """API source types for different markets."""
    TSETMC = "tsetmc"
    TGJU_INDEX = "tgju_index"
    TGJU_STOCK = "tgju_stock"
    TGJU_INDICATOR = "tgju_indicator"
    NFUSION = "nfusion"


@dataclass
class MarketConfig:
    """Configuration for a single market."""
    name: str
    url: str
    source: MarketSource
    instrument_id: str | None = None


# Market configurations
MARKETS: dict[str, MarketConfig] = {
    # TSETMC Markets
    "Sandoghe-Aiar": MarketConfig(
        name="Sandoghe-Aiar",
        url="https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/{id}/0",
        source=MarketSource.TSETMC,
        instrument_id="34144395039913458",
    ),
    "Salam": MarketConfig(
        name="Salam",
        url="https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/{id}/0",
        source=MarketSource.TSETMC,
        instrument_id="70541934393301867",
    ),
    "Energy": MarketConfig(
        name="Energy",
        url="https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/{id}/0",
        source=MarketSource.TSETMC,
        instrument_id="49641108336531623",
    ),
    "Synergy": MarketConfig(
        name="Synergy",
        url="https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/{id}/0",
        source=MarketSource.TSETMC,
        instrument_id="15001802434062073",
    ),
    # TGJU Index Markets
    "Bourse": MarketConfig(
        name="Bourse",
        url="https://api.tgju.org/v1/stocks/instrument/history-data/%D8%B4-%DA%A9%D9%84-%D8%A8%D9%88%D8%B1%D8%B3",
        source=MarketSource.TGJU_INDEX,
    ),
    "Fara-Bourse": MarketConfig(
        name="Fara-Bourse",
        url="https://api.tgju.org/v1/stocks/instrument/history-data/%D8%B4-%DA%A9%D9%84-%D9%81%D8%B1%D8%A7%D8%A8%D9%88%D8%B1%D8%B3",
        source=MarketSource.TGJU_INDEX,
    ),
    "Bourse-Khodro": MarketConfig(
        name="Bourse-Khodro",
        url="https://api.tgju.org/v1/stocks/instrument/history-data/%D8%B4-%D8%AE%D9%88%D8%AF%D8%B1%D9%88%D8%B3%D8%A7%D8%B2%DB%8C",
        source=MarketSource.TGJU_INDEX,
    ),
    # TGJU Stock Markets
    "Khesapa": MarketConfig(
        name="Khesapa",
        url="https://api.tgju.org/v1/stocks/instrument/history-data/خساپا",
        source=MarketSource.TGJU_STOCK,
    ),
    "Khodro": MarketConfig(
        name="Khodro",
        url="https://api.tgju.org/v1/stocks/instrument/history-data/خودرو",
        source=MarketSource.TGJU_STOCK,
    ),
    # TGJU Indicator Markets
    "Dollar": MarketConfig(
        name="Dollar",
        url="https://api.tgju.org/v1/market/indicator/summary-table-data/price_dollar_rl",
        source=MarketSource.TGJU_INDICATOR,
    ),
    "Coin": MarketConfig(
        name="Coin",
        url="https://api.tgju.org/v1/market/indicator/summary-table-data/sekee",
        source=MarketSource.TGJU_INDICATOR,
    ),
    "Nim-Coin": MarketConfig(
        name="Nim-Coin",
        url="https://api.tgju.org/v1/market/indicator/summary-table-data/nim",
        source=MarketSource.TGJU_INDICATOR,
    ),
    "Coin-Gerami": MarketConfig(
        name="Coin-Gerami",
        url="https://api.tgju.org/v1/market/indicator/summary-table-data/gerami",
        source=MarketSource.TGJU_INDICATOR,
    ),
    "Bitcoin": MarketConfig(
        name="Bitcoin",
        url="https://api.tgju.org/v1/market/indicator/summary-table-data/crypto-bitcoin",
        source=MarketSource.TGJU_INDICATOR,
    ),
    "Rob-Coin": MarketConfig(
        name="Rob-Coin",
        url="https://api.tgju.org/v1/market/indicator/summary-table-data/rob",
        source=MarketSource.TGJU_INDICATOR,
    ),
    # NFusion Markets
    "Silver": MarketConfig(
        name="Silver",
        url="https://widget.nfusionsolutions.com/api/v1/Data/history",
        source=MarketSource.NFUSION,
    ),
}


class BaseFetcher(ABC):
    """Abstract base class for market data fetchers."""

    TIMEOUT = 30
    MAX_RETRIES = 3

    @abstractmethod
    def fetch(self, config: MarketConfig) -> pd.DataFrame:
        """Fetch data for a market configuration."""
        pass

    def _request_get(self, url: str, params: dict | None = None) -> dict:
        """Make a GET request with retry logic."""
        for attempt in range(self.MAX_RETRIES):
            try:
                response = requests.get(url, params=params, timeout=self.TIMEOUT)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == self.MAX_RETRIES - 1:
                    raise
        return {}

    def _request_post(
        self, url: str, data: dict, headers: dict | None = None
    ) -> dict:
        """Make a POST request with retry logic."""
        for attempt in range(self.MAX_RETRIES):
            try:
                response = requests.post(
                    url, data=data, headers=headers, timeout=self.TIMEOUT
                )
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == self.MAX_RETRIES - 1:
                    raise
        return {}

    @staticmethod
    def _to_dataframe(
        closing: list, jalali_date: list, market_name: str
    ) -> pd.DataFrame:
        """Create standardized DataFrame from parsed data."""
        return pd.DataFrame({
            "closing": closing,
            "jalali_date": jalali_date,
            "market_type": market_name,
        })


class TSETMCFetcher(BaseFetcher):
    """Fetcher for Tehran Stock Exchange (TSETMC) API."""

    def fetch(self, config: MarketConfig) -> pd.DataFrame:
        url = config.url.format(id=config.instrument_id)
        data = self._request_get(url)

        records = data.get("closingPriceDaily", [])
        if not records:
            logger.warning(f"No data for {config.name}")
            return pd.DataFrame()

        closing = []
        jalali_dates = []

        for record in records:
            closing.append(record.get("pClosing"))
            deven = str(record.get("dEven", ""))
            if len(deven) >= 8:
                jalali_date = JalaliDate.to_jalali(
                    int(deven[:4]), int(deven[4:6]), int(deven[6:8])
                )
                jalali_dates.append(jalali_date.strftime("%Y/%m/%d"))
            else:
                jalali_dates.append("")

        return self._to_dataframe(closing, jalali_dates, config.name)


class TGJUFetcher(BaseFetcher):
    """Fetcher for TGJU API (indexes, stocks, indicators)."""

    # Patterns for parsing HTML values
    PATTERNS = {
        "low_high": re.compile(r'<span class="(?:low|high)" dir="ltr">([\d%,]+)<'),
        "million": re.compile(r'([\d.,]+)\s*<span class="currency-type">میلیون</span>'),
        "price": re.compile(
            r'<span class="label">قیمت:</span><span class="value">([\d.,]+)</span>',
            re.DOTALL,
        ),
    }

    def fetch(self, config: MarketConfig) -> pd.DataFrame:
        params = self._get_params(config.source)
        data = self._request_get(config.url, params=params)

        records = data.get("data", [])
        if not records:
            logger.warning(f"No data for {config.name}")
            return pd.DataFrame()

        return self._parse_records(records, config)

    def _get_params(self, source: MarketSource) -> dict:
        """Get query parameters based on source type."""
        base_params = {"order_dir": "asc", "lang": "fa"}

        if source == MarketSource.TGJU_INDEX:
            return {**base_params, "market": "index"}
        elif source == MarketSource.TGJU_STOCK:
            return {**base_params, "market": "stock"}
        elif source == MarketSource.TGJU_INDICATOR:
            return {**base_params, "convert_to_ad": "1"}

        return base_params

    def _parse_records(
        self, records: list, config: MarketConfig
    ) -> pd.DataFrame:
        """Parse records based on source type."""
        closing = []
        jalali_dates = []

        if config.source == MarketSource.TGJU_INDEX:
            # Format: [jalali, closing, lowest, highest]
            for row in records:
                jalali_dates.append(self._clean_value(row[0]))
                closing.append(self._parse_number(self._clean_value(row[1])))

        elif config.source == MarketSource.TGJU_STOCK:
            # Format: [jalali, a, b, closing, c]
            for row in records:
                jalali_dates.append(self._clean_value(row[0]))
                closing.append(self._parse_number(self._clean_value(row[3])))

        elif config.source == MarketSource.TGJU_INDICATOR:
            # Format: [opening, lowest, highest, closing, ..., jalali]
            for row in records:
                jalali_dates.append(self._clean_value(row[-1]))
                closing.append(self._parse_number(self._clean_value(row[3])))

        return self._to_dataframe(closing, jalali_dates, config.name)

    def _clean_value(self, value: Any) -> str | None:
        """Clean HTML and special characters from value."""
        if value is None or value == "-" or value == "":
            return None

        value = str(value)

        # Check for low/high spans
        match = self.PATTERNS["low_high"].search(value)
        if match:
            number = match.group(1).replace(",", "")
            return f"-{number}" if 'class="low"' in value else number

        # Check for million values
        match = self.PATTERNS["million"].search(value)
        if match:
            number = float(match.group(1).replace(",", ""))
            return str(int(number * 1_000_000))

        # Check for price labels
        match = self.PATTERNS["price"].search(value)
        if match:
            return match.group(1).replace(",", "")

        return value.strip()

    @staticmethod
    def _parse_number(value: str | None) -> float | None:
        """Parse string to number."""
        if value is None:
            return None
        try:
            return float(str(value).replace(",", ""))
        except ValueError:
            return None


class NFusionFetcher(BaseFetcher):
    """Fetcher for NFusion Solutions API (Silver prices)."""

    # Note: Token may need to be refreshed periodically
    DEFAULT_TOKEN = os.getenv(
        "NFUSION_TOKEN",
        "eyJhbGciOiJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzA0L3htbGRzaWctbW9yZSNobWFjLXNoYTI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwczovL3NjaGVtYXMubmZ1c2lvbnNvbHV0aW9ucy5jb20vMjAxOC8wNC9pZGVudGl0eS9jbGFpbXMvY2xpZW50aWQiOiI2ZTk4YWU5OS1kODc4LTQzYTItODFmMC1hMjUyOGJkM2Q0N2UiLCJodHRwczovL3NjaGVtYXMubmZ1c2lvbnNvbHV0aW9ucy5jb20vMjAxOC8wNC9pZGVudGl0eS9jbGFpbXMvaW5zdGFuY2UiOiIwOWY2MzBkOS02MTllLTQzY2ItYWQ2Yy05NDFmMTZlY2MxZWMiLCJleHAiOjE3MzQ3NjU1NTcsImlzcyI6Imh0dHBzOi8vd2lkZ2V0cy5uZnVzaW9uc29sdXRpb25zLmJpei8iLCJhdWQiOiJodHRwczovL3dpZGdldHMubmZ1c2lvbnNvbHV0aW9ucy5iaXovIn0.8NjkmJXG8_IbBkGM2xOg-YjNpvrfN96_WEKjlQomIKE"
    )

    def fetch(self, config: MarketConfig) -> pd.DataFrame:
        headers = {
            "authorization": f"Bearer {self.DEFAULT_TOKEN}",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        }

        data = {
            "clientId": "6e98ae99-d878-43a2-81f0-a2528bd3d47e",
            "instance": "09f630d9-619e-43cb-ad6c-941f16ecc1ec",
            "customId": "",
            "widgetVersion": "1",
            "widgetType": "chart",
            "symbols": "silver",
            "currency": "USD",
            "unitOfMeasure": "toz",
            "timeframeType": "year",
        }

        response_data = self._request_post(config.url, data=data, headers=headers)

        if not response_data or not response_data[0].get("intervals"):
            logger.warning(f"No data for {config.name}")
            return pd.DataFrame()

        records = response_data[0]["intervals"]

        closing = []
        jalali_dates = []

        for record in records:
            closing.append(record.get("last"))
            start_date = record.get("start", "")[:10]
            if start_date:
                try:
                    year, month, day = map(int, start_date.split("-"))
                    jalali_date = JalaliDate.to_jalali(year, month, day)
                    jalali_dates.append(jalali_date.strftime("%Y/%m/%d"))
                except (ValueError, TypeError):
                    jalali_dates.append("")
            else:
                jalali_dates.append("")

        return self._to_dataframe(closing, jalali_dates, config.name)


class MarketDataFetcher:
    """Main class for fetching market data from all sources."""

    def __init__(self):
        self._fetchers: dict[MarketSource, BaseFetcher] = {
            MarketSource.TSETMC: TSETMCFetcher(),
            MarketSource.TGJU_INDEX: TGJUFetcher(),
            MarketSource.TGJU_STOCK: TGJUFetcher(),
            MarketSource.TGJU_INDICATOR: TGJUFetcher(),
            MarketSource.NFUSION: NFusionFetcher(),
        }

    def fetch_market(self, market_name: str) -> pd.DataFrame:
        """
        Fetch data for a single market.

        Args:
            market_name: Name of the market to fetch.

        Returns:
            DataFrame with columns: closing, jalali_date, market_type
        """
        if market_name not in MARKETS:
            logger.error(f"Unknown market: {market_name}")
            return pd.DataFrame()

        config = MARKETS[market_name]
        fetcher = self._fetchers.get(config.source)

        if not fetcher:
            logger.error(f"No fetcher for source: {config.source}")
            return pd.DataFrame()

        try:
            return fetcher.fetch(config)
        except Exception as e:
            logger.error(f"Error fetching {market_name}: {e}")
            return pd.DataFrame()

    def fetch_all(
        self, markets: list[str] | None = None
    ) -> pd.DataFrame:
        """
        Fetch data for multiple markets.

        Args:
            markets: List of market names. If None, fetches all.

        Returns:
            Combined DataFrame with all market data.
        """
        if markets is None:
            markets = list(MARKETS.keys())

        all_data = []

        for market_name in markets:
            logger.info(f"Fetching {market_name}...")
            df = self.fetch_market(market_name)
            if not df.empty:
                all_data.append(df)

        if not all_data:
            return pd.DataFrame()

        return pd.concat(all_data, ignore_index=True)


# Database operations

def update_database(
    df: pd.DataFrame,
    db_file: str = DB_FILE,
    table_name: str = "market_data",
) -> int:
    """
    Update the database with new market data, avoiding duplicates.

    Args:
        df: DataFrame with new market data.
        db_file: Path to SQLite database.
        table_name: Name of the table to update.

    Returns:
        Number of new records inserted.
    """
    with get_db_connection(db_file) as conn:
        try:
            existing = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            existing = existing.drop(columns=["id"], errors="ignore")
        except Exception:
            existing = pd.DataFrame()

        if not existing.empty:
            merged = df.merge(existing, how="outer", indicator=True)
            new_data = merged[merged["_merge"] == "left_only"].drop(columns="_merge")
        else:
            new_data = df

        if not new_data.empty:
            new_data.to_sql(table_name, conn, if_exists="append", index=False)
            logger.info(f"Inserted {len(new_data)} new records.")
            return len(new_data)

        logger.info("No new records to insert.")
        return 0


def remove_duplicates(
    db_file: str = DB_FILE, table_name: str = "market_data"
) -> None:
    """
    Remove duplicate records from the database.

    Keeps the first occurrence of each (market_type, jalali_date) pair.
    """
    query = f"""
    DELETE FROM {table_name} WHERE id IN (
        WITH RankedDuplicates AS (
            SELECT *,
                ROW_NUMBER() OVER (
                    PARTITION BY market_type, jalali_date
                    ORDER BY jalali_date DESC
                ) AS row_num
            FROM {table_name}
            WHERE (market_type, jalali_date) IN (
                SELECT market_type, jalali_date
                FROM {table_name}
                GROUP BY market_type, jalali_date
                HAVING COUNT(*) > 1
            )
        )
        SELECT id FROM RankedDuplicates WHERE row_num >= 2
    );
    """
    with get_db_connection(db_file) as conn:
        conn.execute(query)
        conn.commit()
    logger.info("Duplicates removed.")


# Convenience functions

def fetch_all_markets(
    markets: list[str] | None = None,
    db_file: str = DB_FILE,
) -> pd.DataFrame:
    """
    Fetch data for all markets and update the database.

    Args:
        markets: List of markets to fetch. If None, fetches all.
        db_file: Path to SQLite database.

    Returns:
        Combined DataFrame with all market data.
    """
    fetcher = MarketDataFetcher()
    df = fetcher.fetch_all(markets)

    if not df.empty:
        update_database(df, db_file)
        remove_duplicates(db_file)
        logger.info("Database update completed.")

    return df


def fetch_market(market_name: str) -> pd.DataFrame:
    """
    Fetch data for a single market.

    Args:
        market_name: Name of the market to fetch.

    Returns:
        DataFrame with market data.
    """
    fetcher = MarketDataFetcher()
    return fetcher.fetch_market(market_name)


def get_available_markets() -> list[str]:
    """Return list of all available market names."""
    return list(MARKETS.keys())
