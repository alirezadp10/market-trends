"""
Data fetching module for retrieving market data from various APIs.

This module contains functions to fetch data from:
- TSETMC API (Tehran Stock Exchange)
- TGJU API (Gold, Dollar, Coins, etc.)
- NFusion Solutions API (Silver)
"""

import re

import pandas as pd
import requests
from persiantools.jdatetime import JalaliDate

from .config import DB_FILE
from .data_loader import get_db_connection

# API URLs for different markets
MARKET_URLS = {
    'Sandoghe-Aiar': 'https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/34144395039913458/0',
    'Bourse': 'https://api.tgju.org/v1/stocks/instrument/history-data/%D8%B4-%DA%A9%D9%84-%D8%A8%D9%88%D8%B1%D8%B3?order_dir=asc&market=index',
    'Fara-Bourse': 'https://api.tgju.org/v1/stocks/instrument/history-data/%D8%B4-%DA%A9%D9%84-%D9%81%D8%B1%D8%A7%D8%A8%D9%88%D8%B1%D8%B3?order_dir=asc&market=index',
    'Bourse-Khodro': 'https://api.tgju.org/v1/stocks/instrument/history-data/%D8%B4-%D8%AE%D9%88%D8%AF%D8%B1%D9%88%D8%B3%D8%A7%D8%B2%DB%8C?order_dir=asc&market=index',
    'Khesapa': 'https://api.tgju.org/v1/stocks/instrument/history-data/خساپا?order_dir=asc&market=stock&lang=fa',
    'Khodro': 'https://api.tgju.org/v1/stocks/instrument/history-data/خودرو?order_dir=asc&market=stock&lang=fa',
    'Dollar': 'https://api.tgju.org/v1/market/indicator/summary-table-data/price_dollar_rl?lang=fa&order_dir=asc&convert_to_ad=1',
    'Coin': 'https://api.tgju.org/v1/market/indicator/summary-table-data/sekee?lang=fa&order_dir=asc&convert_to_ad=1',
    'Nim-Coin': 'https://api.tgju.org/v1/market/indicator/summary-table-data/nim?lang=fa&order_dir=asc&convert_to_ad=1',
    'Coin-Gerami': 'https://api.tgju.org/v1/market/indicator/summary-table-data/gerami?lang=fa&order_dir=asc&convert_to_ad=1',
    'Bitcoin': 'https://api.tgju.org/v1/market/indicator/summary-table-data/crypto-bitcoin?lang=fa&order_dir=asc&convert_to_ad=1',
    'Rob-Coin': 'https://api.tgju.org/v1/market/indicator/summary-table-data/rob?lang=fa&order_dir=asc&convert_to_ad=1',
    'Silver': 'https://widget.nfusionsolutions.com/api/v1/Data/history',
    'Salam': 'https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/70541934393301867/0',
    'Energy': 'https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/49641108336531623/0',
    'Synergy': 'https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/15001802434062073/0',
}

# Markets that use TSETMC API
TSETMC_MARKETS = {'Sandoghe-Aiar', 'Salam', 'Energy', 'Synergy'}

# Markets that use stock index format
STOCK_INDEX_MARKETS = {'Bourse', 'Fara-Bourse', 'Bourse-Khodro'}

# Markets that use individual stock format
INDIVIDUAL_STOCK_MARKETS = {'Khesapa', 'Khodro'}


def clean_value(value: str) -> str | float | int | None:
    """
    Clean and parse values from API responses.

    Handles various formats including:
    - Empty or dash values
    - HTML spans with low/high classes
    - Million (میلیون) currency values
    - Price labels

    Args:
        value: Raw value string from API.

    Returns:
        Cleaned value as appropriate type.
    """
    if value == '-' or not value:
        return None

    # Extract value from "low" or "high" spans
    match = re.search(r'<span class="(?:low|high)" dir="ltr">([\d%,]+)<', value)
    if match:
        number = match.group(1).replace(',', '')
        return f'-{number}' if 'class="low"' in value else number

    # Handle "میلیون" (million) values
    match = re.search(r'([\d.,]+)\s*<span class="currency-type">میلیون</span>', value)
    if match:
        number = float(match.group(1).replace(',', ''))
        return int(number * 1_000_000)

    # Handle price labels
    match = re.search(
        r'<span class="label">قیمت:</span><span class="value">([\d.,]+)</span>',
        value,
        re.DOTALL,
    )
    if match:
        return float(match.group(1).replace(',', ''))

    return value.strip()


def fetch_data(url: str) -> dict:
    """
    Fetch JSON data from a URL.

    Args:
        url: URL to fetch from.

    Returns:
        JSON response as dictionary.

    Raises:
        requests.HTTPError: If the request fails.
    """
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_silver_data(url: str) -> dict:
    """
    Fetch silver price data from NFusion Solutions API.

    Args:
        url: NFusion Solutions API URL.

    Returns:
        JSON response as dictionary.
    """
    headers = {
        "authorization": "Bearer eyJhbGciOiJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzA0L3htbGRzaWctbW9yZSNobWFjLXNoYTI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwczovL3NjaGVtYXMubmZ1c2lvbnNvbHV0aW9ucy5jb20vMjAxOC8wNC9pZGVudGl0eS9jbGFpbXMvY2xpZW50aWQiOiI2ZTk4YWU5OS1kODc4LTQzYTItODFmMC1hMjUyOGJkM2Q0N2UiLCJodHRwczovL3NjaGVtYXMubmZ1c2lvbnNvbHV0aW9ucy5jb20vMjAxOC8wNC9pZGVudGl0eS9jbGFpbXMvaW5zdGFuY2UiOiIwOWY2MzBkOS02MTllLTQzY2ItYWQ2Yy05NDFmMTZlY2MxZWMiLCJleHAiOjE3MzQ3NjU1NTcsImlzcyI6Imh0dHBzOi8vd2lkZ2V0cy5uZnVzaW9uc29sdXRpb25zLmJpei8iLCJhdWQiOiJodHRwczovL3dpZGdldHMubmZ1c2lvbnNvbHV0aW9ucy5iaXovIn0.8NjkmJXG8_IbBkGM2xOg-YjNpvrfN96_WEKjlQomIKE",
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

    response = requests.post(url, headers=headers, data=data, timeout=30)
    response.raise_for_status()
    return response.json()


def process_market_data(market_name: str, url: str) -> pd.DataFrame:
    """
    Fetch and process market data into a standardized DataFrame.

    Args:
        market_name: Name of the market to fetch.
        url: API URL for the market.

    Returns:
        DataFrame with columns: closing, jalali_date, market_type
    """
    # Fetch raw data
    if market_name == 'Silver':
        raw_data = fetch_silver_data(url)
    else:
        raw_data = fetch_data(url)

    # Extract data array based on market type
    if market_name in TSETMC_MARKETS:
        raw_data = raw_data.get('closingPriceDaily', [])
    elif market_name == 'Silver':
        raw_data = raw_data[0]['intervals']
    else:
        raw_data = raw_data.get('data', [])

    if not raw_data:
        print(f"No data available for {market_name}")
        return pd.DataFrame()

    # Define columns based on market type
    if market_name in STOCK_INDEX_MARKETS:
        columns = ['jalali', 'closing', 'lowest', 'highest']
    elif market_name in TSETMC_MARKETS:
        columns = [
            'priceChange', 'priceMin', 'priceMax', 'priceYesterday', 'priceFirst',
            'last', 'id', 'insCode', 'dEven', 'hEven', 'pClosing', 'iClose',
            'yClose', 'pDrCotVal', 'zTotTran', 'qTotTran5J', 'qTotCap'
        ]
    elif market_name in INDIVIDUAL_STOCK_MARKETS:
        columns = ['jalali', 'a', 'b', 'closing', 'c']
    elif market_name == 'Silver':
        columns = ['start', 'end', 'open', 'high', 'low', 'last']
    else:
        columns = [
            'opening', 'lowest', 'highest', 'closing', 'change_amount',
            'change_percentage', 'gregorian_date', 'jalali'
        ]

    # Clean values for non-TSETMC and non-Silver markets
    if market_name not in TSETMC_MARKETS and market_name != 'Silver':
        raw_data = [[clean_value(item) for item in row] for row in raw_data]

    df = pd.DataFrame(raw_data, columns=columns[:len(raw_data[0])])

    # Standardize DataFrame
    if 'closing' in df.columns:
        df['closing'] = df['closing'].replace({',': ''}, regex=True).astype(float)
        df.rename({'jalali': 'jalali_date'}, axis=1, inplace=True)

    if market_name in TSETMC_MARKETS:
        df['dEven'] = df['dEven'].apply(
            lambda x: JalaliDate.to_jalali(
                int(str(x)[:4]), int(str(x)[4:6]), int(str(x)[6:8])
            ).strftime('%Y/%m/%d')
        )
        df.rename({'dEven': 'jalali_date', 'pClosing': 'closing'}, axis=1, inplace=True)

    if market_name == 'Silver':
        df['jalali_date'] = df['start'].apply(
            lambda x: JalaliDate.to_jalali(
                *map(int, x[:10].split('-'))
            ).strftime('%Y/%m/%d')
        )
        df.rename({'last': 'closing'}, axis=1, inplace=True)

    df['market_type'] = market_name

    return df[['closing', 'jalali_date', 'market_type']].fillna('')


def update_database(
    df: pd.DataFrame,
    db_file: str = DB_FILE,
    table_name: str = 'market_data',
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
            existing_data = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            existing_data = existing_data.drop(columns=["id"], errors='ignore')
        except Exception:
            existing_data = pd.DataFrame()

        if not existing_data.empty:
            new_data = df.merge(
                existing_data, how='outer', indicator=True
            ).query('_merge == "left_only"').drop(columns='_merge')
        else:
            new_data = df

        if not new_data.empty:
            new_data.to_sql(table_name, conn, if_exists='append', index=False)
            print(f"Inserted {len(new_data)} new records.")
            return len(new_data)
        else:
            print("No new records to insert.")
            return 0


def remove_duplicates(db_file: str = DB_FILE, table_name: str = 'market_data') -> None:
    """
    Remove duplicate records from the database.

    Keeps the first occurrence of each (market_type, jalali_date) pair.

    Args:
        db_file: Path to SQLite database.
        table_name: Name of the table to clean.
    """
    query = f"""
    DELETE FROM {table_name} WHERE id in (
        WITH RankedDuplicates AS (
            SELECT *,
                ROW_NUMBER() OVER (
                    PARTITION BY market_type, jalali_date
                    ORDER BY jalali_date desc
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
    if markets is None:
        markets = list(MARKET_URLS.keys())

    all_data_frames = []

    for market_name in markets:
        if market_name not in MARKET_URLS:
            print(f"Unknown market: {market_name}")
            continue

        url = MARKET_URLS[market_name]
        try:
            market_df = process_market_data(market_name, url)
            if not market_df.empty:
                all_data_frames.append(market_df)
        except Exception as e:
            print(f"Error fetching {market_name}: {e}")

    if not all_data_frames:
        return pd.DataFrame()

    final_df = pd.concat(all_data_frames, ignore_index=True)

    # Update database
    update_database(final_df, db_file)

    # Remove duplicates
    remove_duplicates(db_file)

    print("Database update completed.")
    return final_df
