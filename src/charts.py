"""
Plotting functions for market data visualization.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from IPython.display import display, HTML

from .config import COLORS, MARKET_NAMES


def set_custom_output_height(height: int = 800) -> None:
    """
    Set custom height for Jupyter notebook output cells.

    Args:
        height: Height in pixels.
    """
    display(HTML(f'<style>.output {{ height: {height}px; overflow-y: scroll; }}</style>'))


def plot_stacked_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: str,
    title: str,
    labels: dict | None = None,
    height: int = 800,
) -> go.Figure:
    """
    Create a stacked bar chart using Plotly Express.

    Args:
        df: DataFrame containing the data.
        x_col: Column name for the x-axis.
        y_col: Column name for the y-axis.
        color_col: Column name for the color grouping.
        title: Chart title.
        labels: Custom labels for axis and legend.
        height: Chart height in pixels.

    Returns:
        Plotly Figure object.
    """
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title,
        labels=labels or {},
        barmode="stack",
        text=y_col,
        height=height,
    )

    fig.update_layout(
        xaxis=dict(
            title=x_col.capitalize(),
            categoryorder="array",
            categoryarray=sorted(df[x_col].unique()),
            tickangle=0
        ),
        yaxis=dict(title=y_col.capitalize()),
        legend_title=color_col.capitalize(),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    fig.update_traces(texttemplate='%{text:.2f}', textposition='inside')
    fig.show()

    return fig


def plot_correlation_heatmap(
    df: pd.DataFrame,
    date_col: str = 'jalali_date',
    market_col: str = 'market_type',
    value_col: str = 'closing',
    markets: list[str] | None = None,
    height: int = 800,
    title: str = "هیت‌مپ همبستگی بازارها",
) -> go.Figure:
    """
    Create a correlation heatmap between markets.

    Args:
        df: DataFrame with market data.
        date_col: Column containing dates.
        market_col: Column containing market types.
        value_col: Column containing values.
        markets: List of markets to include.
        height: Chart height.
        title: Chart title.

    Returns:
        Plotly Figure object.
    """
    pivot_df = df.copy()

    if markets:
        pivot_df = pivot_df[pivot_df[market_col].isin(markets)]

    # Translate market names to Persian
    pivot_df[market_col] = pivot_df[market_col].apply(
        lambda x: MARKET_NAMES.get(str(x), 'Unknown')
    )

    # Create pivot table
    pivot_df = pivot_df.pivot(
        index=date_col,
        columns=market_col,
        values=value_col
    )

    correlation_matrix = pivot_df.corr()

    fig = px.imshow(
        correlation_matrix,
        text_auto=True,
        labels=dict(x="بازار", y="بازار", color="همبستگی"),
        x=correlation_matrix.columns,
        y=correlation_matrix.index,
        color_continuous_scale="Viridis"
    )

    fig.update_layout(
        title=title,
        height=height,
        xaxis_title="بازار",
        yaxis_title="بازار"
    )

    fig.show()
    return fig


def plot_data_existence(
    df: pd.DataFrame,
    date_col: str = 'jalali_year_month',
    market_col: str = 'market_type',
    value_col: str = 'closing',
    exclude_markets: list[str] | None = None,
    height: int = 800,
) -> go.Figure:
    """
    Create a heatmap showing data availability by market and time period.

    Args:
        df: DataFrame with market data.
        date_col: Column containing date grouping.
        market_col: Column containing market types.
        value_col: Column to count.
        exclude_markets: Markets to exclude from the heatmap.
        height: Chart height.

    Returns:
        Plotly Figure object.
    """
    plot_df = df.copy()

    if exclude_markets:
        plot_df = plot_df[~plot_df[market_col].isin(exclude_markets)]

    # Prepare heatmap data
    heatmap_data = plot_df.groupby([market_col, date_col])[value_col].count().reset_index()
    heatmap_pivot = heatmap_data.pivot(
        index=market_col,
        columns=date_col,
        values=value_col
    ).fillna(0)

    fig = px.imshow(
        heatmap_pivot,
        labels=dict(x="Year-Month", y="Market Type", color="Count"),
        title="Density of Closing Count by Year-Month and Market Type",
        color_continuous_scale="Viridis",
        aspect="auto"
    )

    fig.update_layout(
        xaxis_title="Year-Month",
        yaxis_title="Market Type",
        title_font_size=16,
        height=height,
        xaxis=dict(tickangle=90)
    )

    fig.show()
    return fig


def plot_market_comparison(
    df: pd.DataFrame,
    markets: list[str],
    date_filter: "JalaliDate",
    date_type: str = 'jalali',
    aggregation_type: str = 'monthly',
    events_df: pd.DataFrame | None = None,
    height: int = 800,
) -> go.Figure:
    """
    Create a line chart comparing percentage change across markets.

    Args:
        df: DataFrame with market data.
        markets: List of market types to compare.
        date_filter: Start date for filtering.
        date_type: 'jalali' or 'gregorian'.
        aggregation_type: 'monthly' or 'daily'.
        events_df: Optional DataFrame with events for annotations.
        height: Chart height.

    Returns:
        Plotly Figure object.
    """
    import pandas as pd

    date_column = f'{date_type}_date'
    date_group_col = f'{date_type}_year_month' if aggregation_type == 'monthly' else date_column

    monthly_data_dict = {}

    for market_type in df['market_type'].unique():
        if market_type not in markets:
            continue

        market_data = df[df['market_type'] == market_type]
        market_data = market_data[market_data[date_column] >= date_filter]

        if market_data.empty:
            continue

        grouped = market_data.groupby(date_group_col).agg(
            avg_closing_price=('closing', 'mean')
        )

        if grouped.empty:
            continue

        grouped['price_change_in_percentage'] = (
            grouped['avg_closing_price'] / grouped['avg_closing_price'].iloc[0] - 1
        ) * 100

        market_name = MARKET_NAMES.get(str(market_type), 'Unknown')
        monthly_data_dict[market_name] = {
            date_group_col: grouped.index.tolist(),
            'price_change_in_percentage': grouped['price_change_in_percentage'].tolist(),
        }

    fig = go.Figure()

    for name, data in monthly_data_dict.items():
        hover_texts = []
        marker_colors = []
        marker_sizes = []

        for date in data[date_group_col]:
            if events_df is not None:
                matching = events_df[events_df['Date'] == date]
                if not matching.empty:
                    event_names = "<br>".join(matching['Event'].tolist())
                    hover_texts.append(f"<b>{event_names}</b>")
                    marker_colors.append('yellow')
                    marker_sizes.append(2)
                    continue

            hover_texts.append("")
            marker_colors.append('rgba(0,0,0,0)')
            marker_sizes.append(0)

        fig.add_trace(go.Scatter(
            x=data[date_group_col],
            y=data['price_change_in_percentage'],
            mode='lines+markers',
            name=name,
            hoverinfo="text",
            text=hover_texts,
            marker=dict(
                color=marker_colors,
                size=marker_sizes,
                line=dict(width=1, color="darkred")
            ),
            line=dict(color=COLORS.get(name, "black"), width=2)
        ))

    x_title = "Date (Month to Month)" if aggregation_type == 'monthly' else "Date (Daily)"

    fig.update_layout(
        title="Percentage Change by Market",
        xaxis_title=x_title,
        yaxis_title="Percentage Change",
        xaxis=dict(type="category", tickangle=-90),
        template='plotly_white',
        showlegend=True,
        height=height
    )

    fig.show()
    return fig


def plot_market_trend(
    df: pd.DataFrame,
    market: str,
    start_date: "JalaliDate | None" = None,
    height: int = 800,
) -> go.Figure:
    """
    Create a simple line chart for a single market.

    Args:
        df: DataFrame with market data.
        market: Market type to plot.
        start_date: Optional start date for filtering.
        height: Chart height.

    Returns:
        Plotly Figure object.
    """
    market_df = df[df['market_type'] == market].copy()

    if start_date:
        market_df = market_df[market_df['jalali_date'] >= start_date]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=market_df['jalali_date'].apply(lambda x: x.strftime('%Y/%m/%d')),
        y=market_df['closing'],
    ))

    fig.update_layout(
        template='plotly_white',
        title_font_size=16,
        height=height,
    )

    fig.show()
    return fig


def plot_yearly_trends_subplots(
    df: pd.DataFrame,
    market: str,
    year_col: str = 'jalali_year',
    month_col: str = 'jalali_month',
    value_col: str = 'closing',
    columns: int = 2,
) -> go.Figure:
    """
    Create subplots showing monthly trends for each year.

    Args:
        df: DataFrame with market data.
        market: Market type to plot.
        year_col: Column containing year.
        month_col: Column containing month.
        value_col: Column containing values.
        columns: Number of columns in subplot grid.

    Returns:
        Plotly Figure object.
    """
    market_df = df[df['market_type'] == market]

    monthly_avg = market_df.groupby([year_col, month_col]).agg(
        avg_closing_price=(value_col, 'mean')
    ).reset_index()

    unique_years = monthly_avg[year_col].unique()
    num_years = len(unique_years)
    rows = (num_years + columns - 1) // columns

    fig = make_subplots(
        rows=rows,
        cols=columns,
        subplot_titles=[f'Average Monthly Closing Price for {year}' for year in unique_years]
    )

    for idx, year in enumerate(unique_years):
        yearly_data = monthly_avg[monthly_avg[year_col] == year]

        row = idx // columns + 1
        col = idx % columns + 1

        fig.add_trace(
            go.Scatter(
                x=yearly_data[month_col],
                y=yearly_data['avg_closing_price'],
                mode='lines+markers',
                name=f'Year {year}',
                line=dict(width=2),
                marker=dict(size=6)
            ),
            row=row, col=col
        )

    fig.update_layout(
        template='plotly_white',
        title='Average Monthly Closing Prices',
        showlegend=False,
        height=300 * rows,
        xaxis_title='Month',
        yaxis_title='Average Closing Price',
    )

    fig.show()
    return fig


def plot_rankings_heatmap(
    df: pd.DataFrame,
    year_col: str = 'jalali_year',
    rank_col: str = 'rank',
    growth_col: str = 'growth_rate',
    market_col: str = 'market_type',
    height: int = 800,
    title: str = "Market Rankings by Year",
) -> go.Figure:
    """
    Create a heatmap showing market rankings over time.

    Args:
        df: DataFrame with ranking data.
        year_col: Column containing year.
        rank_col: Column containing rank.
        growth_col: Column containing growth rate.
        market_col: Column containing market type.
        height: Chart height.
        title: Chart title.

    Returns:
        Plotly Figure object.
    """
    heatmap_data = df.pivot(index=market_col, columns=year_col, values=rank_col)
    growth_data = df.pivot(index=market_col, columns=year_col, values=growth_col)

    fig = px.imshow(
        heatmap_data,
        labels={"x": "Year", "y": "Market Type", "color": "Rank"},
        title=title,
        text_auto=True,
    )

    fig.update_traces(
        hovertemplate=(
            "Market Type: %{y}<br>"
            "Year: %{x}<br>"
            "Rank: %{z}<br>"
            "Growth Rate: %{customdata}"
        ),
        customdata=growth_data.values
    )

    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        height=height
    )

    fig.show()
    return fig
