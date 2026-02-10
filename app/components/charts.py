"""
Chart components for SQN Trust dashboard.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# SQN Trust color palette
COLORS = {
    "primary": "#1a365d",      # Deep navy
    "secondary": "#2d5a87",    # Medium blue
    "accent": "#48a9a6",       # Teal
    "success": "#38a169",      # Green
    "warning": "#d69e2e",      # Gold
    "danger": "#c53030",       # Red
    "muted": "#718096",        # Gray
    "light": "#f7fafc",        # Light gray
    "background": "#ffffff"
}

ASSET_COLORS = {
    "Shares": "#2d5a87",
    "RealEstate": "#48a9a6",
    "Liquid": "#d69e2e"
}

REGION_COLORS = {
    "US": "#1a365d",
    "EU": "#2d5a87",
    "HU": "#48a9a6",
    "Global": "#718096"
}

def get_chart_layout(**overrides):
    """Get chart layout with optional overrides."""
    base = {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Inter, sans-serif", "color": "#1a365d"},
        "margin": {"l": 50, "r": 30, "t": 40, "b": 40},
        "hovermode": "x unified",
        "height": 280
    }
    base.update(overrides)
    return base


def create_allocation_donut(allocation_df: pd.DataFrame, title: str = "Asset Allocation") -> go.Figure:
    """
    Create asset allocation donut chart.
    
    Args:
        allocation_df: DataFrame with 'asset_type', 'value', 'percentage' columns
        title: Chart title
    
    Returns:
        Plotly figure
    """
    if allocation_df.empty:
        return go.Figure().update_layout(
            annotations=[{"text": "No data", "showarrow": False}],
            **get_chart_layout()
        )
    
    colors = [ASSET_COLORS.get(t, COLORS["muted"]) for t in allocation_df["asset_type"]]
    
    fig = go.Figure(data=[go.Pie(
        labels=allocation_df["asset_type"],
        values=allocation_df["value"],
        hole=0.65,
        marker={"colors": colors},
        textinfo="label+percent",
        textposition="outside",
        textfont={"size": 11},
        hovertemplate="<b>%{label}</b><br>€%{value:,.0f}<br>%{percent}<extra></extra>"
    )])
    
    # Add center annotation
    total = allocation_df["value"].sum()
    fig.add_annotation(
        text=f"<b>€{total/1_000_000:.1f}M</b><br><span style='font-size:10px'>Total Value</span>",
        x=0.5, y=0.5,
        font={"size": 14, "color": COLORS["primary"]},
        showarrow=False
    )
    
    fig.update_layout(
        showlegend=False,
        **get_chart_layout(margin={"l": 20, "r": 20, "t": 30, "b": 20}, height=300)
    )
    
    return fig


def create_nav_line_chart(nav_df: pd.DataFrame, title: str = "Portfolio Value") -> go.Figure:
    """
    Create NAV line chart.
    
    Args:
        nav_df: DataFrame with 'date' and 'value' columns
        title: Chart title
    
    Returns:
        Plotly figure
    """
    if nav_df.empty:
        return go.Figure().update_layout(
            annotations=[{"text": "No data", "showarrow": False}],
            **get_chart_layout()
        )
    
    fig = go.Figure()
    
    # Add area fill
    fig.add_trace(go.Scatter(
        x=nav_df["date"],
        y=nav_df["value"],
        fill="tozeroy",
        fillcolor="rgba(45, 90, 135, 0.1)",
        line={"color": COLORS["secondary"], "width": 2},
        mode="lines",
        name="Portfolio Value",
        hovertemplate="<b>%{x|%b %d, %Y}</b><br>€%{y:,.0f}<extra></extra>"
    ))
    
    fig.update_layout(
        title={"text": title, "font": {"size": 14}},
        xaxis={
            "showgrid": False,
            "showline": True,
            "linecolor": "#e2e8f0"
        },
        yaxis={
            "showgrid": True,
            "gridcolor": "#f0f4f8",
            "showline": False,
            "tickprefix": "€",
            "tickformat": ",.0f"
        },
        **get_chart_layout(height=300)
    )
    
    return fig


def create_region_bar_chart(region_df: pd.DataFrame, title: str = "Regional Exposure") -> go.Figure:
    """
    Create horizontal bar chart for regional exposure.
    
    Args:
        region_df: DataFrame with 'region', 'value', 'percentage' columns
        title: Chart title
    
    Returns:
        Plotly figure
    """
    if region_df.empty:
        return go.Figure().update_layout(
            annotations=[{"text": "No data", "showarrow": False}],
            **get_chart_layout()
        )
    
    colors = [REGION_COLORS.get(r, COLORS["muted"]) for r in region_df["region"]]
    
    fig = go.Figure(data=[go.Bar(
        x=region_df["percentage"],
        y=region_df["region"],
        orientation="h",
        marker={"color": colors},
        text=[f"{p:.1f}%" for p in region_df["percentage"]],
        textposition="inside",
        textfont={"color": "white", "size": 11},
        hovertemplate="<b>%{y}</b><br>€%{customdata:,.0f}<br>%{x:.1f}%<extra></extra>",
        customdata=region_df["value"]
    )])
    
    fig.update_layout(
        title={"text": title, "font": {"size": 14}},
        xaxis={
            "showgrid": False,
            "showticklabels": False,
            "range": [0, 100]
        },
        yaxis={
            "showgrid": False,
            "categoryorder": "total ascending"
        },
        **get_chart_layout(height=200, margin={"l": 60, "r": 20, "t": 40, "b": 20})
    )
    
    return fig


def create_sector_bar_chart(sector_df: pd.DataFrame, title: str = "Sector Allocation") -> go.Figure:
    """
    Create horizontal bar chart for sector allocation.
    
    Args:
        sector_df: DataFrame with 'sector', 'value', 'percentage' columns
        title: Chart title
    
    Returns:
        Plotly figure
    """
    if sector_df.empty:
        return go.Figure().update_layout(
            annotations=[{"text": "No data", "showarrow": False}],
            **get_chart_layout()
        )
    
    # Take top 8 sectors
    sector_df = sector_df.head(8)
    
    fig = go.Figure(data=[go.Bar(
        x=sector_df["percentage"],
        y=sector_df["sector"],
        orientation="h",
        marker={"color": COLORS["secondary"]},
        text=[f"{p:.1f}%" for p in sector_df["percentage"]],
        textposition="inside",
        textfont={"color": "white", "size": 11},
        hovertemplate="<b>%{y}</b><br>€%{customdata:,.0f}<br>%{x:.1f}%<extra></extra>",
        customdata=sector_df["value"]
    )])
    
    fig.update_layout(
        title={"text": title, "font": {"size": 14}},
        xaxis={
            "showgrid": False,
            "showticklabels": False,
            "range": [0, max(sector_df["percentage"]) * 1.2]
        },
        yaxis={
            "showgrid": False,
            "categoryorder": "total ascending"
        },
        **get_chart_layout(height=250, margin={"l": 120, "r": 20, "t": 40, "b": 20})
    )
    
    return fig


def create_drawdown_chart(drawdown_df: pd.DataFrame, title: str = "Drawdown") -> go.Figure:
    """
    Create drawdown area chart.
    
    Args:
        drawdown_df: DataFrame with 'date' and 'drawdown_pct' columns
        title: Chart title
    
    Returns:
        Plotly figure
    """
    if drawdown_df.empty:
        return go.Figure().update_layout(
            annotations=[{"text": "No data", "showarrow": False}],
            **get_chart_layout()
        )
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=drawdown_df["date"],
        y=drawdown_df["drawdown_pct"],
        fill="tozeroy",
        fillcolor="rgba(197, 48, 48, 0.2)",
        line={"color": COLORS["danger"], "width": 1.5},
        mode="lines",
        name="Drawdown",
        hovertemplate="<b>%{x|%b %d, %Y}</b><br>%{y:.1f}%<extra></extra>"
    ))
    
    fig.update_layout(
        title={"text": title, "font": {"size": 14}},
        xaxis={
            "showgrid": False,
            "showline": True,
            "linecolor": "#e2e8f0"
        },
        yaxis={
            "showgrid": True,
            "gridcolor": "#f0f4f8",
            "showline": False,
            "ticksuffix": "%",
            "range": [min(drawdown_df["drawdown_pct"]) * 1.1, 0]
        },
        **get_chart_layout(height=250)
    )
    
    return fig


def create_monthly_returns_bar(monthly_df: pd.DataFrame, title: str = "Monthly Returns") -> go.Figure:
    """
    Create monthly returns bar chart.
    
    Args:
        monthly_df: DataFrame with 'month' and 'return_pct' columns
        title: Chart title
    
    Returns:
        Plotly figure
    """
    if monthly_df.empty:
        return go.Figure().update_layout(
            annotations=[{"text": "No data", "showarrow": False}],
            **get_chart_layout()
        )
    
    # Take last 24 months
    monthly_df = monthly_df.tail(24)
    
    colors = [COLORS["success"] if r >= 0 else COLORS["danger"] for r in monthly_df["return_pct"]]
    
    fig = go.Figure(data=[go.Bar(
        x=monthly_df["month"],
        y=monthly_df["return_pct"],
        marker={"color": colors},
        hovertemplate="<b>%{x}</b><br>%{y:.1f}%<extra></extra>"
    )])
    
    fig.update_layout(
        title={"text": title, "font": {"size": 14}},
        xaxis={
            "showgrid": False,
            "tickangle": -45,
            "dtick": 3
        },
        yaxis={
            "showgrid": True,
            "gridcolor": "#f0f4f8",
            "ticksuffix": "%",
            "zeroline": True,
            "zerolinecolor": "#1a365d",
            "zerolinewidth": 1
        },
        **get_chart_layout(height=300)
    )
    
    return fig


def create_cashflow_chart(cashflow_df: pd.DataFrame, title: str = "Monthly Cashflows") -> go.Figure:
    """
    Create stacked bar chart for cashflows.
    
    Args:
        cashflow_df: DataFrame with 'month', 'inflows', 'outflows', 'net' columns
        title: Chart title
    
    Returns:
        Plotly figure
    """
    if cashflow_df.empty:
        return go.Figure().update_layout(
            annotations=[{"text": "No data", "showarrow": False}],
            **get_chart_layout()
        )
    
    # Take last 12 months
    cashflow_df = cashflow_df.tail(12)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=cashflow_df["month"],
        y=cashflow_df["inflows"],
        name="Inflows",
        marker={"color": COLORS["success"]},
        hovertemplate="<b>%{x}</b><br>Inflows: €%{y:,.0f}<extra></extra>"
    ))
    
    fig.add_trace(go.Bar(
        x=cashflow_df["month"],
        y=-cashflow_df["outflows"],
        name="Outflows",
        marker={"color": COLORS["danger"]},
        hovertemplate="<b>%{x}</b><br>Outflows: €%{y:,.0f}<extra></extra>"
    ))
    
    fig.update_layout(
        title={"text": title, "font": {"size": 14}},
        barmode="relative",
        xaxis={
            "showgrid": False,
            "tickangle": -45
        },
        yaxis={
            "showgrid": True,
            "gridcolor": "#f0f4f8",
            "tickprefix": "€",
            "tickformat": ",.0f"
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1
        },
        **get_chart_layout(height=300)
    )
    
    return fig


def create_property_type_donut(holdings_df: pd.DataFrame, title: str = "Property Types") -> go.Figure:
    """
    Create property type donut chart for real estate.
    
    Args:
        holdings_df: Holdings DataFrame
        title: Chart title
    
    Returns:
        Plotly figure
    """
    real_estate = holdings_df[holdings_df["asset_type"] == "RealEstate"]
    
    if real_estate.empty:
        return go.Figure().update_layout(
            annotations=[{"text": "No data", "showarrow": False}],
            **get_chart_layout()
        )
    
    allocation = real_estate.groupby("property_type")["valuation_current"].sum().reset_index()
    
    property_colors = {
        "Residential": "#2d5a87",
        "Commercial": "#48a9a6",
        "Retail": "#d69e2e",
        "Industrial": "#718096",
        "Mixed-Use": "#1a365d"
    }
    
    colors = [property_colors.get(t, COLORS["muted"]) for t in allocation["property_type"]]
    
    fig = go.Figure(data=[go.Pie(
        labels=allocation["property_type"],
        values=allocation["valuation_current"],
        hole=0.6,
        marker={"colors": colors},
        textinfo="label+percent",
        textposition="outside",
        textfont={"size": 11},
        hovertemplate="<b>%{label}</b><br>€%{value:,.0f}<br>%{percent}<extra></extra>"
    )])
    
    fig.update_layout(
        title={"text": title, "font": {"size": 14}},
        showlegend=False,
        **get_chart_layout(height=250, margin={"l": 20, "r": 20, "t": 40, "b": 20})
    )
    
    return fig


def create_geography_bar(holdings_df: pd.DataFrame, title: str = "Real Estate by Country") -> go.Figure:
    """
    Create bar chart for real estate by country.
    
    Args:
        holdings_df: Holdings DataFrame
        title: Chart title
    
    Returns:
        Plotly figure
    """
    real_estate = holdings_df[holdings_df["asset_type"] == "RealEstate"]
    
    if real_estate.empty:
        return go.Figure().update_layout(
            annotations=[{"text": "No data", "showarrow": False}],
            **get_chart_layout()
        )
    
    allocation = real_estate.groupby("country")["valuation_current"].sum().reset_index()
    allocation = allocation.sort_values("valuation_current", ascending=True)
    
    fig = go.Figure(data=[go.Bar(
        x=allocation["valuation_current"],
        y=allocation["country"],
        orientation="h",
        marker={"color": COLORS["accent"]},
        hovertemplate="<b>%{y}</b><br>€%{x:,.0f}<extra></extra>"
    )])
    
    fig.update_layout(
        title={"text": title, "font": {"size": 14}},
        xaxis={
            "showgrid": False,
            "tickprefix": "€",
            "tickformat": ",.0f"
        },
        yaxis={
            "showgrid": False
        },
        **get_chart_layout(height=200, margin={"l": 40, "r": 20, "t": 40, "b": 20})
    )
    
    return fig


def create_account_breakdown_donut(holdings_df: pd.DataFrame, accounts_df: pd.DataFrame) -> go.Figure:
    """
    Create account breakdown donut chart for liquid assets.
    
    Args:
        holdings_df: Holdings DataFrame
        accounts_df: Accounts DataFrame
        
    Returns:
        Plotly figure
    """
    liquid = holdings_df[holdings_df["asset_type"] == "Liquid"]
    
    if liquid.empty:
        return go.Figure().update_layout(
            annotations=[{"text": "No data", "showarrow": False}],
            **get_chart_layout()
        )
    
    allocation = liquid.groupby("account_id")["valuation_current"].sum().reset_index()
    
    # Merge with account names
    allocation = allocation.merge(accounts_df[["account_id", "account_name"]], on="account_id")
    
    fig = go.Figure(data=[go.Pie(
        labels=allocation["account_name"],
        values=allocation["valuation_current"],
        hole=0.6,
        marker={"colors": px.colors.qualitative.Set2},
        textinfo="label+percent",
        textposition="outside",
        textfont={"size": 10},
        hovertemplate="<b>%{label}</b><br>€%{value:,.0f}<br>%{percent}<extra></extra>"
    )])
    
    fig.update_layout(
        title={"text": "Liquid Assets by Account", "font": {"size": 14}},
        showlegend=False,
        **get_chart_layout(height=250, margin={"l": 20, "r": 20, "t": 40, "b": 20})
    )
    
    return fig


def create_performance_comparison_chart(
    nav_df: pd.DataFrame,
    accounts_df: pd.DataFrame,
    title: str = "Performance by Account"
) -> go.Figure:
    """
    Create multi-line chart comparing account performance.
    
    Args:
        nav_df: Full NAV DataFrame with per-account columns
        accounts_df: Accounts DataFrame
        title: Chart title
    
    Returns:
        Plotly figure
    """
    if nav_df.empty:
        return go.Figure().update_layout(
            annotations=[{"text": "No data", "showarrow": False}],
            **get_chart_layout()
        )
    
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set2
    
    for i, (_, account) in enumerate(accounts_df.iterrows()):
        value_col = f"value_{account['account_id']}"
        if value_col in nav_df.columns:
            # Normalize to 100 at start
            values = nav_df[value_col].values
            normalized = (values / values[0]) * 100
            
            fig.add_trace(go.Scatter(
                x=nav_df["date"],
                y=normalized,
                name=account["account_name"],
                mode="lines",
                line={"color": colors[i % len(colors)], "width": 2},
                hovertemplate=f"<b>{account['account_name']}</b><br>%{{x|%b %d, %Y}}<br>%{{y:.1f}}<extra></extra>"
            ))
    
    fig.update_layout(
        title={"text": title, "font": {"size": 14}},
        xaxis={
            "showgrid": False,
            "showline": True,
            "linecolor": "#e2e8f0"
        },
        yaxis={
            "showgrid": True,
            "gridcolor": "#f0f4f8",
            "title": "Indexed (100 = Start)"
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1
        },
        **get_chart_layout(height=350)
    )
    
    return fig

