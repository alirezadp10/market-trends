import sqlite3
from contextlib import contextmanager
from pathlib import Path

import pandas as pd

from .config import DB_FILE, EVENTS_FILE, MARKET_NAMES


@contextmanager
def get_db_connection(db_file: str = DB_FILE):
    """Context manager for database connections."""
    conn = sqlite3.connect(db_file)
    try:
        yield conn
    finally:
        conn.close()


def load_market_data(
    db_file: str = DB_FILE,
    market_types: list[str] | None = None,
) -> pd.DataFrame:
    """
    Load market data from SQLite database.

    Args:
        db_file: Path to the SQLite database file.
        market_types: List of market types to load. If None, loads all markets
                     defined in MARKET_NAMES.

    Returns:
        DataFrame with market data.
    """
    if market_types is None:
        market_types = list(MARKET_NAMES.keys())

    placeholders = ", ".join(f"'{key}'" for key in market_types)
    query = f"SELECT * FROM market_data WHERE market_type IN ({placeholders})"

    with get_db_connection(db_file) as conn:
        df = pd.read_sql_query(query, conn)

    return df


def load_events(events_file: str = EVENTS_FILE) -> pd.DataFrame:
    """
    Load events data from CSV file.

    Args:
        events_file: Path to the events CSV file.

    Returns:
        DataFrame with events data.
    """
    return pd.read_csv(events_file)


def save_market_data(
    df: pd.DataFrame,
    db_file: str = DB_FILE,
    table_name: str = "market_data",
    if_exists: str = "append",
) -> int:
    """
    Save market data to SQLite database.

    Args:
        df: DataFrame to save.
        db_file: Path to the SQLite database file.
        table_name: Name of the table to save to.
        if_exists: How to behave if the table exists ('append', 'replace', 'fail').

    Returns:
        Number of rows inserted.
    """
    with get_db_connection(db_file) as conn:
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)
        return len(df)
