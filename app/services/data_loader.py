"""
Data loading and caching service for SQN Trust dashboard.
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any

import pandas as pd

# Data directory path
DATA_DIR = Path(__file__).parent.parent / "data"


@lru_cache(maxsize=1)
def load_client() -> Dict[str, Any]:
    """Load client profile from JSON."""
    with open(DATA_DIR / "client.json", "r") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_accounts() -> pd.DataFrame:
    """Load accounts data."""
    return pd.read_csv(DATA_DIR / "accounts.csv")


@lru_cache(maxsize=1)
def load_holdings() -> pd.DataFrame:
    """Load holdings data."""
    df = pd.read_csv(DATA_DIR / "holdings.csv")
    df["last_valuation_date"] = pd.to_datetime(df["last_valuation_date"])
    return df


@lru_cache(maxsize=1)
def load_transactions() -> pd.DataFrame:
    """Load transactions data."""
    df = pd.read_csv(DATA_DIR / "transactions.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df


@lru_cache(maxsize=1)
def load_nav() -> pd.DataFrame:
    """Load NAV time series data."""
    df = pd.read_csv(DATA_DIR / "nav.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df


@lru_cache(maxsize=1)
def load_ownership() -> Dict[str, Any]:
    """Load company ownership data from JSON."""
    ownership_file = DATA_DIR / "ownership.json"
    if ownership_file.exists():
        with open(ownership_file, "r") as f:
            return json.load(f)
    return {"companies": []}


@lru_cache(maxsize=1)
def load_real_estate_locations() -> list:
    """Load real estate location data from JSON."""
    locations_file = DATA_DIR / "real_estate_locations.json"
    if locations_file.exists():
        with open(locations_file, "r") as f:
            return json.load(f)
    return []


def get_account_options() -> list:
    """Get account options for dropdown."""
    accounts = load_accounts()
    options = [{"label": "All Accounts", "value": "all"}]
    for _, row in accounts.iterrows():
        options.append({
            "label": f"{row['account_name']} ({row['custodian']})",
            "value": row["account_id"]
        })
    return options


def get_asset_type_options() -> list:
    """Get asset type options for dropdown."""
    return [
        {"label": "All Assets", "value": "all"},
        {"label": "Shares", "value": "Shares"},
        {"label": "Real Estate", "value": "RealEstate"},
        {"label": "Liquid", "value": "Liquid"}
    ]


# FX rates (mock - EUR base)
FX_RATES = {
    "EUR": 1.0,
    "USD": 0.92,
    "HUF": 0.0025,
    "GBP": 1.17,
    "CHF": 1.08
}


def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    """Convert amount between currencies using mock FX rates."""
    if from_currency == to_currency:
        return amount
    
    # Convert to EUR first
    amount_eur = amount * FX_RATES.get(from_currency, 1.0)
    
    # Convert to target currency
    if to_currency == "EUR":
        return amount_eur
    else:
        return amount_eur / FX_RATES.get(to_currency, 1.0)


def reload_data():
    """Clear cache and reload all data."""
    load_client.cache_clear()
    load_accounts.cache_clear()
    load_holdings.cache_clear()
    load_transactions.cache_clear()
    load_nav.cache_clear()
    load_ownership.cache_clear()
    load_real_estate_locations.cache_clear()

