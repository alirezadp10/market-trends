"""
DataFrame transformation and enrichment functions for market data.
"""

import pandas as pd
from persiantools.jdatetime import JalaliDate

from .config import (
    START_DATE,
    END_DATE,
    JALALI_SEASONS,
    GREGORIAN_SEASONS,
    MARKET_NAMES,
)


def convert_persian_to_jalali(persian_date: str) -> JalaliDate:
    """
    Convert a Persian date string to JalaliDate object.

    Args:
        persian_date: Date string in 'YYYY/MM/DD' format.

    Returns:
        JalaliDate object.
    """
    if isinstance(persian_date, str):
        year, month, day = map(int, persian_date.split('/'))
        return JalaliDate(year, month, day)
    return persian_date


def get_season(month: str | int, seasons: list[str]) -> str:
    """
    Get the season name for a given month.

    Args:
        month: Month number (1-12) as string or int.
        seasons: List of 4 season names.

    Returns:
        Season name.
    """
    return seasons[(int(month) - 1) // 3]


def calculate_periods(
    df: pd.DataFrame,
    column: str,
    periods: list[int],
    prefix: str,
) -> pd.DataFrame:
    """
    Calculate period columns for grouping years.

    Args:
        df: DataFrame to modify.
        column: Column name containing year values.
        periods: List of period lengths (e.g., [2, 3, 4]).
        prefix: Prefix for new column names.

    Returns:
        DataFrame with new period columns.
    """
    df = df.copy()
    for period in periods:
        col_name = f"{prefix}_{period}_year_period"
        df[col_name] = df[column].apply(
            lambda x: '-'.join(
                str(y) for y in range(
                    (x // period) * period,
                    (x // period) * period + period
                )
            )
        )
    return df


def enrich_dataframe(
    df: pd.DataFrame,
    start_date: JalaliDate | None = None,
    end_date: JalaliDate | None = None,
) -> pd.DataFrame:
    """
    Enrich market data DataFrame with date-related columns.

    Adds columns for:
    - Jalali date components (year, month, season, weekday)
    - Gregorian date components (year, month, season, weekday)
    - Period groupings (2, 3, 4 year periods)

    Args:
        df: DataFrame with 'jalali_date' column.
        start_date: Start date for filtering. Defaults to config START_DATE.
        end_date: End date for filtering. Defaults to config END_DATE.

    Returns:
        Enriched DataFrame.
    """
    df = df.copy()

    if start_date is None:
        start_date = START_DATE
    if end_date is None:
        end_date = END_DATE

    # Convert Persian dates to Jalali
    df['jalali_date'] = df['jalali_date'].apply(convert_persian_to_jalali)

    # Add Jalali date components
    df['jalali_year'] = df['jalali_date'].apply(lambda x: int(x.strftime('%Y')))
    df['jalali_month'] = df['jalali_date'].apply(lambda x: x.strftime('%m'))
    df['jalali_year_month'] = df['jalali_date'].apply(lambda x: x.strftime('%Y-%m'))
    df['jalali_season'] = df['jalali_month'].apply(
        lambda x: get_season(x, JALALI_SEASONS)
    )
    df['jalali_week_day'] = df['jalali_date'].apply(lambda x: x.strftime('%A'))

    # Calculate Jalali periods
    df = calculate_periods(df, 'jalali_year', [2, 3, 4], 'jalali')

    # Convert to Gregorian and add components
    df['gregorian_date'] = df['jalali_date'].apply(lambda x: x.to_gregorian())
    df['gregorian_date'] = pd.to_datetime(df['gregorian_date'])

    df['gregorian_year'] = df['gregorian_date'].apply(lambda x: int(x.strftime('%Y')))
    df['gregorian_month'] = df['gregorian_date'].apply(lambda x: x.strftime('%m'))
    df['gregorian_year_month'] = df['gregorian_date'].apply(
        lambda x: x.strftime('%Y-%m')
    )
    df['gregorian_season'] = df['gregorian_month'].apply(
        lambda x: get_season(x, GREGORIAN_SEASONS)
    )
    df['gregorian_week_day'] = df['gregorian_date'].apply(lambda x: x.strftime('%A'))

    # Calculate Gregorian periods
    df = calculate_periods(df, 'gregorian_year', [2, 3, 4], 'gregorian')

    # Filter by date range
    df = df[(df['jalali_date'] >= start_date) & (df['jalali_date'] < end_date)]

    return df


def translate_market_names(df: pd.DataFrame, column: str = 'market_type') -> pd.DataFrame:
    """
    Translate market type column from English to Persian.

    Args:
        df: DataFrame with market_type column.
        column: Name of the column to translate.

    Returns:
        DataFrame with translated market names.
    """
    df = df.copy()
    df[column] = df[column].apply(lambda x: MARKET_NAMES.get(str(x), 'Unknown'))
    return df


def calculate_growth_rate(
    df: pd.DataFrame,
    group_cols: list[str],
    value_col: str = 'closing',
) -> pd.DataFrame:
    """
    Calculate growth rate (percentage change) for market data.

    Args:
        df: DataFrame with market data.
        group_cols: Columns to group by (e.g., ['market_type', 'jalali_year']).
        value_col: Column containing values to calculate growth for.

    Returns:
        DataFrame with growth_rate column.
    """
    result = (
        df.groupby(group_cols)
        .agg(growth_rate=(value_col, 'mean'))
        .groupby(level='market_type')['growth_rate']
        .pct_change() * 100
    ).reset_index()
    return result


def calculate_market_rankings(
    df: pd.DataFrame,
    year_col: str = 'jalali_year',
    exclude_years: list[int] | None = None,
) -> pd.DataFrame:
    """
    Calculate yearly market rankings based on growth rate.

    Args:
        df: DataFrame with market data.
        year_col: Column containing year values.
        exclude_years: Years to exclude from ranking.

    Returns:
        DataFrame with rank column.
    """
    if exclude_years is None:
        exclude_years = []

    # Calculate growth rate
    growth_df = calculate_growth_rate(df, ['market_type', year_col])

    # Sort and calculate rank
    growth_df = growth_df.sort_values(
        [year_col, 'growth_rate'],
        ascending=[True, False]
    )
    growth_df['rank'] = growth_df.groupby(year_col)['growth_rate'].rank(
        ascending=False,
        method='dense'
    )

    # Filter out excluded years
    growth_df = growth_df[~growth_df[year_col].isin(exclude_years)]

    return growth_df


def get_top_markets(
    df: pd.DataFrame,
    group_col: str,
    n: int = 5,
) -> pd.DataFrame:
    """
    Get top N markets by growth rate for each group.

    Args:
        df: DataFrame with growth_rate column.
        group_col: Column to group by.
        n: Number of top markets to return per group.

    Returns:
        DataFrame with top N markets per group.
    """
    return (
        df.sort_values([group_col, 'growth_rate'], ascending=[True, False])
        .groupby(group_col, group_keys=False)
        .head(n)
    )


def calculate_seasonal_influence(
    df: pd.DataFrame,
    market_col: str = 'market_type',
    year_col: str = 'jalali_year',
    season_col: str = 'jalali_season',
    value_col: str = 'closing',
) -> pd.DataFrame:
    """
    Calculate seasonal influence percentage for each market.

    Args:
        df: DataFrame with market data.
        market_col: Column containing market type.
        year_col: Column containing year.
        season_col: Column containing season.
        value_col: Column containing values.

    Returns:
        DataFrame with influence_percentage column.
    """
    # Calculate seasonal means
    seasonal = df.groupby([market_col, year_col, season_col]).agg(
        mean_closing=(value_col, 'mean')
    ).reset_index()

    # Calculate yearly totals
    yearly_totals = seasonal.groupby([market_col, year_col])['mean_closing'].sum().reset_index()

    # Merge and calculate percentage
    result = pd.merge(
        seasonal,
        yearly_totals,
        on=[year_col, market_col],
        suffixes=('', '_total')
    )
    result['influence_percentage'] = (
        (result['mean_closing'] / result['mean_closing_total']) * 100
    ).astype(int)

    return result
