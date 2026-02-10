"""
Metrics calculation service for SQN Trust dashboard.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


def calculate_total_value(holdings: pd.DataFrame) -> float:
    """Calculate total portfolio value."""
    if holdings.empty:
        return 0.0
    return holdings["valuation_current"].sum()


def calculate_cost_basis(holdings: pd.DataFrame) -> float:
    """Calculate total cost basis."""
    if holdings.empty:
        return 0.0
    return holdings["valuation_cost_basis"].sum()


def calculate_unrealized_pnl(holdings: pd.DataFrame) -> Tuple[float, float]:
    """
    Calculate unrealized P&L.
    
    Returns:
        Tuple of (absolute P&L, percentage P&L)
    """
    if holdings.empty:
        return (0.0, 0.0)
    
    current = holdings["valuation_current"].sum()
    cost = holdings["valuation_cost_basis"].sum()
    
    pnl_abs = current - cost
    pnl_pct = (pnl_abs / cost * 100) if cost > 0 else 0.0
    
    return (pnl_abs, pnl_pct)


def calculate_returns_from_nav(
    nav: pd.DataFrame,
    period_days: int = 365
) -> Dict[str, float]:
    """
    Calculate returns from NAV series.
    
    Args:
        nav: NAV dataframe with 'date' and 'value' columns
        period_days: Number of days for return calculation
    
    Returns:
        Dictionary with return metrics
    """
    if nav.empty or len(nav) < 2:
        return {
            "return_pct": 0.0,
            "return_abs": 0.0,
            "start_value": 0.0,
            "end_value": 0.0
        }
    
    nav_sorted = nav.sort_values("date")
    end_value = nav_sorted["value"].iloc[-1]
    end_date = nav_sorted["date"].iloc[-1]
    
    # Find value at start of period
    start_date = end_date - pd.Timedelta(days=period_days)
    nav_period = nav_sorted[nav_sorted["date"] >= start_date]
    
    if nav_period.empty:
        nav_period = nav_sorted
    
    start_value = nav_period["value"].iloc[0]
    
    return_pct = ((end_value / start_value) - 1) * 100 if start_value > 0 else 0.0
    return_abs = end_value - start_value
    
    return {
        "return_pct": return_pct,
        "return_abs": return_abs,
        "start_value": start_value,
        "end_value": end_value
    }


def calculate_ytd_return(nav: pd.DataFrame) -> float:
    """Calculate year-to-date return percentage."""
    if nav.empty:
        return 0.0
    
    nav_sorted = nav.sort_values("date")
    end_value = nav_sorted["value"].iloc[-1]
    end_date = nav_sorted["date"].iloc[-1]
    
    # Find first value of current year
    year_start = datetime(end_date.year, 1, 1)
    nav_ytd = nav_sorted[nav_sorted["date"] >= year_start]
    
    if nav_ytd.empty or len(nav_ytd) < 2:
        return 0.0
    
    start_value = nav_ytd["value"].iloc[0]
    
    return ((end_value / start_value) - 1) * 100 if start_value > 0 else 0.0


def calculate_volatility(nav: pd.DataFrame, annualized: bool = True) -> float:
    """
    Calculate portfolio volatility from NAV series.
    
    Args:
        nav: NAV dataframe with 'date' and 'value' columns
        annualized: Whether to annualize the volatility
    
    Returns:
        Volatility (standard deviation of returns)
    """
    if nav.empty or len(nav) < 3:
        return 0.0
    
    nav_sorted = nav.sort_values("date")
    returns = nav_sorted["value"].pct_change().dropna()
    
    if returns.empty:
        return 0.0
    
    std = returns.std()
    
    if annualized:
        # Assume weekly data, annualize
        std = std * np.sqrt(52)
    
    return std * 100  # Return as percentage


def calculate_max_drawdown(nav: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate maximum drawdown from NAV series.
    
    Returns:
        Dictionary with drawdown metrics
    """
    if nav.empty or len(nav) < 2:
        return {
            "max_drawdown_pct": 0.0,
            "peak_value": 0.0,
            "trough_value": 0.0,
            "peak_date": None,
            "trough_date": None
        }
    
    nav_sorted = nav.sort_values("date")
    values = nav_sorted["value"].values
    dates = nav_sorted["date"].values
    
    # Calculate running maximum
    running_max = np.maximum.accumulate(values)
    drawdowns = (values - running_max) / running_max
    
    # Find max drawdown
    max_dd_idx = np.argmin(drawdowns)
    max_drawdown = drawdowns[max_dd_idx]
    
    # Find peak before trough
    peak_idx = np.argmax(values[:max_dd_idx + 1]) if max_dd_idx > 0 else 0
    
    return {
        "max_drawdown_pct": max_drawdown * 100,
        "peak_value": values[peak_idx],
        "trough_value": values[max_dd_idx],
        "peak_date": pd.Timestamp(dates[peak_idx]),
        "trough_date": pd.Timestamp(dates[max_dd_idx])
    }


def calculate_asset_allocation(holdings: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate asset allocation breakdown.
    
    Returns:
        DataFrame with asset type, value, and percentage
    """
    if holdings.empty:
        return pd.DataFrame(columns=["asset_type", "value", "percentage"])
    
    allocation = holdings.groupby("asset_type")["valuation_current"].sum().reset_index()
    allocation.columns = ["asset_type", "value"]
    total = allocation["value"].sum()
    allocation["percentage"] = (allocation["value"] / total * 100) if total > 0 else 0
    
    return allocation.sort_values("value", ascending=False)


def calculate_region_allocation(holdings: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate regional allocation breakdown.
    
    Returns:
        DataFrame with region, value, and percentage
    """
    if holdings.empty:
        return pd.DataFrame(columns=["region", "value", "percentage"])
    
    allocation = holdings.groupby("region")["valuation_current"].sum().reset_index()
    allocation.columns = ["region", "value"]
    total = allocation["value"].sum()
    allocation["percentage"] = (allocation["value"] / total * 100) if total > 0 else 0
    
    return allocation.sort_values("value", ascending=False)


def calculate_sector_allocation(holdings: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate sector allocation breakdown (for Shares only).
    
    Returns:
        DataFrame with sector, value, and percentage
    """
    shares = holdings[holdings["asset_type"] == "Shares"]
    
    if shares.empty:
        return pd.DataFrame(columns=["sector", "value", "percentage"])
    
    allocation = shares.groupby("sector")["valuation_current"].sum().reset_index()
    allocation.columns = ["sector", "value"]
    total = allocation["value"].sum()
    allocation["percentage"] = (allocation["value"] / total * 100) if total > 0 else 0
    
    return allocation.sort_values("value", ascending=False)


def get_top_holdings(holdings: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Get top N holdings by value.
    
    Returns:
        DataFrame with top holdings
    """
    if holdings.empty:
        return pd.DataFrame()
    
    top = holdings.nlargest(n, "valuation_current").copy()
    top["unrealized_pnl"] = top["valuation_current"] - top["valuation_cost_basis"]
    top["unrealized_pnl_pct"] = (
        (top["valuation_current"] / top["valuation_cost_basis"] - 1) * 100
    )
    
    return top[["asset_name", "asset_type", "region", "valuation_current", 
                "valuation_cost_basis", "unrealized_pnl", "unrealized_pnl_pct"]]


def calculate_concentration(holdings: pd.DataFrame, top_n: int = 3) -> float:
    """
    Calculate concentration metric (top N holdings % of portfolio).
    
    Returns:
        Percentage of portfolio in top N holdings
    """
    if holdings.empty:
        return 0.0
    
    total = holdings["valuation_current"].sum()
    top_values = holdings.nlargest(top_n, "valuation_current")["valuation_current"].sum()
    
    return (top_values / total * 100) if total > 0 else 0.0


def calculate_liquidity_score(holdings: pd.DataFrame) -> float:
    """
    Calculate weighted average liquidity score.
    
    Returns:
        Average liquidity score (0-1)
    """
    if holdings.empty:
        return 0.0
    
    total_value = holdings["valuation_current"].sum()
    if total_value == 0:
        return 0.0
    
    # Handle both old numeric and new enum liquidity
    if "liquidity" in holdings.columns and holdings["liquidity"].dtype == "object":
        # Convert enum to numeric: Large=0.9, Moderate=0.5, Small=0.2
        liquidity_map = {"Large": 0.9, "Moderate": 0.5, "Small": 0.2}
        liquidity_values = holdings["liquidity"].map(liquidity_map).fillna(0.5)
        weighted_liquidity = (liquidity_values * holdings["valuation_current"]).sum()
    elif "liquidity_score" in holdings.columns:
        weighted_liquidity = (
            holdings["liquidity_score"] * holdings["valuation_current"]
        ).sum()
    else:
        return 0.5  # Default
    
    return weighted_liquidity / total_value


def calculate_cash_percentage(holdings: pd.DataFrame) -> float:
    """
    Calculate cash/liquid allocation percentage.
    
    Returns:
        Percentage of portfolio in liquid assets
    """
    if holdings.empty:
        return 0.0
    
    total = holdings["valuation_current"].sum()
    liquid = holdings[holdings["asset_type"] == "Liquid"]["valuation_current"].sum()
    
    return (liquid / total * 100) if total > 0 else 0.0


def generate_insights(
    holdings: pd.DataFrame,
    nav: pd.DataFrame,
    client: Dict,
    months_lookback: int = 3,
    currency_symbol: str = "€"
) -> List[Dict[str, str]]:
    """
    Generate portfolio insights.
    
    Args:
        holdings: Holdings DataFrame
        nav: NAV DataFrame
        client: Client dictionary
        months_lookback: Months to look back for analysis
        currency_symbol: Currency symbol to display
    
    Returns:
        List of insight dictionaries with 'title' and 'text'
    """
    insights = []
    
    if holdings.empty:
        return [{"title": "No Data", "text": "No holdings data available."}]
    
    # Biggest position
    biggest = holdings.nlargest(1, "valuation_current").iloc[0]
    total = holdings["valuation_current"].sum()
    biggest_pct = (biggest["valuation_current"] / total * 100) if total > 0 else 0
    insights.append({
        "title": "Largest Position",
        "text": f"{biggest['asset_name']} represents {biggest_pct:.1f}% of your portfolio "
                f"({currency_symbol}{biggest['valuation_current']:,.0f})."
    })
    
    # Biggest mover (by P&L percentage)
    holdings_pnl = holdings.copy()
    holdings_pnl["pnl_pct"] = (
        (holdings_pnl["valuation_current"] / holdings_pnl["valuation_cost_basis"] - 1) * 100
    )
    
    best_performer = holdings_pnl.nlargest(1, "pnl_pct").iloc[0]
    worst_performer = holdings_pnl.nsmallest(1, "pnl_pct").iloc[0]
    
    insights.append({
        "title": "Best Performer",
        "text": f"{best_performer['asset_name']} has gained {best_performer['pnl_pct']:.1f}% "
                f"since purchase."
    })
    
    if worst_performer["pnl_pct"] < 0:
        insights.append({
            "title": "Underperformer",
            "text": f"{worst_performer['asset_name']} is down {abs(worst_performer['pnl_pct']):.1f}% "
                    f"from cost basis."
        })
    
    # Allocation vs target
    target_allocation = client.get("target_allocation", {})
    if target_allocation:
        allocation = calculate_asset_allocation(holdings)
        allocation_dict = dict(zip(allocation["asset_type"], allocation["percentage"]))
        
        drifts = []
        for asset_type, target_pct in target_allocation.items():
            actual_pct = allocation_dict.get(asset_type, 0)
            drift = actual_pct - (target_pct * 100)
            if abs(drift) > 5:
                direction = "overweight" if drift > 0 else "underweight"
                drifts.append(f"{asset_type} is {abs(drift):.1f}pp {direction}")
        
        if drifts:
            insights.append({
                "title": "Allocation Drift",
                "text": f"Your portfolio has drifted from target allocation: {'; '.join(drifts)}."
            })
        else:
            insights.append({
                "title": "Allocation Status",
                "text": "Your portfolio is well-aligned with your target allocation."
            })
    
    # Liquidity assessment
    avg_liquidity = calculate_liquidity_score(holdings)
    if avg_liquidity >= 0.7:
        liquidity_text = "highly liquid"
    elif avg_liquidity >= 0.4:
        liquidity_text = "moderately liquid"
    else:
        liquidity_text = "less liquid with longer exit horizons"
    
    insights.append({
        "title": "Liquidity Profile",
        "text": f"Your portfolio is {liquidity_text} with an average liquidity score of "
                f"{avg_liquidity:.0%}."
    })
    
    # Concentration warning
    concentration = calculate_concentration(holdings, 3)
    if concentration > 30:
        insights.append({
            "title": "Concentration Alert",
            "text": f"Your top 3 positions represent {concentration:.1f}% of the portfolio. "
                    f"Consider diversification."
        })
    
    return insights


def downsample_nav(nav: pd.DataFrame, max_points: int = 150) -> pd.DataFrame:
    """
    Downsample NAV data to reduce chart rendering time.
    
    Args:
        nav: NAV dataframe with 'date' and 'value' columns
        max_points: Maximum number of data points to keep
    
    Returns:
        Downsampled NAV dataframe
    """
    if nav.empty or len(nav) <= max_points:
        return nav
    
    # Keep every nth row to reduce to max_points
    step = len(nav) // max_points
    downsampled = nav.iloc[::step].copy()
    
    # Always include the last row for accurate current value
    if nav.index[-1] not in downsampled.index:
        downsampled = pd.concat([downsampled, nav.iloc[[-1]]])
    
    return downsampled.reset_index(drop=True)


def calculate_monthly_returns(nav: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate monthly returns from NAV series.
    
    Returns:
        DataFrame with month and return percentage
    """
    if nav.empty or len(nav) < 2:
        return pd.DataFrame(columns=["month", "return_pct"])
    
    nav_sorted = nav.sort_values("date").copy()
    nav_sorted["month"] = nav_sorted["date"].dt.to_period("M")
    
    # Get first and last value of each month
    monthly = nav_sorted.groupby("month").agg({
        "value": ["first", "last"]
    })
    monthly.columns = ["start_value", "end_value"]
    monthly["return_pct"] = (
        (monthly["end_value"] / monthly["start_value"] - 1) * 100
    )
    
    monthly = monthly.reset_index()
    monthly["month"] = monthly["month"].astype(str)
    
    return monthly[["month", "return_pct"]]


def calculate_drawdown_series(nav: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate drawdown time series.
    
    Returns:
        DataFrame with date and drawdown percentage
    """
    if nav.empty or len(nav) < 2:
        return pd.DataFrame(columns=["date", "drawdown_pct"])
    
    nav_sorted = nav.sort_values("date").copy()
    values = nav_sorted["value"].values
    
    # Calculate running maximum
    running_max = np.maximum.accumulate(values)
    drawdowns = (values - running_max) / running_max * 100
    
    result = pd.DataFrame({
        "date": nav_sorted["date"],
        "drawdown_pct": drawdowns
    })
    
    return result


def calculate_cashflow_summary(transactions: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate monthly cashflow summary.
    
    Returns:
        DataFrame with month, inflows, outflows, and net
    """
    if transactions.empty:
        return pd.DataFrame(columns=["month", "inflows", "outflows", "net"])
    
    tx = transactions.copy()
    tx["month"] = tx["date"].dt.to_period("M")
    
    # Classify transactions
    tx["inflow"] = tx["amount"].apply(lambda x: x if x > 0 else 0)
    tx["outflow"] = tx["amount"].apply(lambda x: abs(x) if x < 0 else 0)
    
    monthly = tx.groupby("month").agg({
        "inflow": "sum",
        "outflow": "sum"
    }).reset_index()
    
    monthly.columns = ["month", "inflows", "outflows"]
    monthly["net"] = monthly["inflows"] - monthly["outflows"]
    monthly["month"] = monthly["month"].astype(str)
    
    return monthly


def calculate_income_summary(transactions: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate income summary (dividends, rent, interest).
    
    Returns:
        Dictionary with income breakdown
    """
    if transactions.empty:
        return {"dividends": 0, "rent": 0, "interest": 0, "total": 0}
    
    dividends = transactions[transactions["type"] == "dividend"]["amount"].sum()
    rent = transactions[transactions["type"] == "rent"]["amount"].sum()
    interest = transactions[transactions["type"] == "interest"]["amount"].sum()
    
    return {
        "dividends": dividends,
        "rent": rent,
        "interest": interest,
        "total": dividends + rent + interest
    }

