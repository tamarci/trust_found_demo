"""
Filter service for SQN Trust dashboard.
Applies global filters to data across all tabs.
"""

from datetime import datetime
from typing import Optional, Tuple

import pandas as pd


def filter_holdings(
    holdings: pd.DataFrame,
    account_id: Optional[str] = None,
    asset_type: Optional[str] = None,
    date_range: Optional[Tuple[datetime, datetime]] = None
) -> pd.DataFrame:
    """
    Apply filters to holdings dataframe.
    
    Args:
        holdings: Holdings dataframe
        account_id: Account ID or 'all'
        asset_type: Asset type or 'all'
        date_range: Tuple of (start_date, end_date)
    
    Returns:
        Filtered holdings dataframe
    """
    df = holdings.copy()
    
    # Filter by account
    if account_id and account_id != "all":
        df = df[df["account_id"] == account_id]
    
    # Filter by asset type
    if asset_type and asset_type != "all":
        df = df[df["asset_type"] == asset_type]
    
    # Filter by valuation date
    if date_range:
        start_date, end_date = date_range
        if start_date:
            df = df[df["last_valuation_date"] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df["last_valuation_date"] <= pd.to_datetime(end_date)]
    
    return df


def filter_transactions(
    transactions: pd.DataFrame,
    account_id: Optional[str] = None,
    tx_type: Optional[str] = None,
    date_range: Optional[Tuple[datetime, datetime]] = None
) -> pd.DataFrame:
    """
    Apply filters to transactions dataframe.
    
    Args:
        transactions: Transactions dataframe
        account_id: Account ID or 'all'
        tx_type: Transaction type or 'all'
        date_range: Tuple of (start_date, end_date)
    
    Returns:
        Filtered transactions dataframe
    """
    df = transactions.copy()
    
    # Filter by account
    if account_id and account_id != "all":
        df = df[df["account_id"] == account_id]
    
    # Filter by transaction type
    if tx_type and tx_type != "all":
        df = df[df["type"] == tx_type]
    
    # Filter by date range
    if date_range:
        start_date, end_date = date_range
        if start_date:
            df = df[df["date"] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df["date"] <= pd.to_datetime(end_date)]
    
    return df


def filter_nav(
    nav: pd.DataFrame,
    account_id: Optional[str] = None,
    date_range: Optional[Tuple[datetime, datetime]] = None
) -> pd.DataFrame:
    """
    Apply filters to NAV dataframe.
    
    Args:
        nav: NAV dataframe
        account_id: Account ID or 'all'
        date_range: Tuple of (start_date, end_date)
    
    Returns:
        Filtered NAV dataframe with 'value' column
    """
    df = nav.copy()
    
    # Filter by date range
    if date_range:
        start_date, end_date = date_range
        if start_date:
            df = df[df["date"] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df["date"] <= pd.to_datetime(end_date)]
    
    # Select value column based on account
    if account_id and account_id != "all":
        value_col = f"value_{account_id}"
        if value_col in df.columns:
            df["value"] = df[value_col]
        else:
            df["value"] = df["total_value"]
    else:
        df["value"] = df["total_value"]
    
    return df[["date", "value"]].copy()


def get_date_range_options():
    """Get predefined date range options."""
    return [
        {"label": "1 Month", "value": "1M"},
        {"label": "3 Months", "value": "3M"},
        {"label": "6 Months", "value": "6M"},
        {"label": "1 Year", "value": "1Y"},
        {"label": "All Time", "value": "ALL"}
    ]


def parse_date_range(period: str, reference_date: datetime = None) -> Tuple[datetime, datetime]:
    """
    Parse date range string to datetime tuple.
    
    Args:
        period: Period string ('1M', '3M', '6M', '1Y', 'ALL')
        reference_date: Reference date (defaults to today)
    
    Returns:
        Tuple of (start_date, end_date)
    """
    if reference_date is None:
        reference_date = datetime.now()
    
    end_date = reference_date
    
    if period == "1M":
        start_date = end_date - pd.DateOffset(months=1)
    elif period == "3M":
        start_date = end_date - pd.DateOffset(months=3)
    elif period == "6M":
        start_date = end_date - pd.DateOffset(months=6)
    elif period == "1Y":
        start_date = end_date - pd.DateOffset(years=1)
    else:  # ALL
        start_date = datetime(2020, 1, 1)
    
    return (start_date, end_date)

