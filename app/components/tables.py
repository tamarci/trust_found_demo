"""
Table components for SQN Trust dashboard.
"""

import dash_bootstrap_components as dbc
from dash import html, dash_table
import pandas as pd
from services.translations import t


# Base table styling (without style_data_conditional for extension)
TABLE_STYLE_BASE = {
    "style_table": {
        "overflowX": "auto",
        "borderRadius": "8px",
        "border": "1px solid #e2e8f0"
    },
    "style_header": {
        "backgroundColor": "#f7fafc",
        "fontWeight": "600",
        "color": "#1a365d",
        "borderBottom": "2px solid #e2e8f0",
        "padding": "12px 16px",
        "textAlign": "left",
        "fontSize": "0.75rem",
        "textTransform": "uppercase",
        "letterSpacing": "0.5px"
    },
    "style_cell": {
        "padding": "12px 16px",
        "backgroundColor": "#ffffff",
        "color": "#2d3748",
        "fontSize": "0.875rem",
        "border": "none",
        "textAlign": "left"
    },
    "style_data": {
        "borderBottom": "1px solid #f0f4f8"
    }
}

# Default conditional styling
DEFAULT_CONDITIONAL = [
    {
        "if": {"row_index": "odd"},
        "backgroundColor": "#fafbfc"
    },
    {
        "if": {"state": "selected"},
        "backgroundColor": "#ebf4ff",
        "border": "1px solid #3182ce"
    }
]


def create_top_holdings_table(holdings_df: pd.DataFrame, lang: str = "en", currency_symbol: str = "€", n: int = 10) -> html.Div:
    """
    Create top holdings table.
    
    Args:
        holdings_df: Holdings DataFrame
        lang: Language code ('en' or 'hu')
        currency_symbol: Currency symbol to display
        n: Number of holdings to show
    
    Returns:
        Dash table component
    """
    if holdings_df.empty:
        return html.Div(
            html.P(t("no_data", lang), className="text-muted text-center py-4"),
            className="border rounded"
        )
    
    # Prepare data
    top = holdings_df.nlargest(n, "valuation_current").copy()
    top["unrealized_pnl"] = top["valuation_current"] - top["valuation_cost_basis"]
    top["unrealized_pnl_pct"] = (
        (top["valuation_current"] / top["valuation_cost_basis"] - 1) * 100
    )
    
    # Column names based on language
    col_labels = {
        "en": {"asset": "Asset", "type": "Type", "region": "Region", "value": "Value", "pnl": "P&L", "pnl_pct": "P&L %"},
        "hu": {"asset": "Eszköz", "type": "Típus", "region": "Régió", "value": "Érték", "pnl": "Profit/Veszt.", "pnl_pct": "Profit/Veszt. %"}
    }
    labels = col_labels.get(lang, col_labels["en"])
    
    # Format for display
    display_df = pd.DataFrame({
        labels["asset"]: top["asset_name"],
        labels["type"]: top["asset_type"],
        labels["region"]: top["region"],
        labels["value"]: top["valuation_current"].apply(lambda x: f"{currency_symbol}{x:,.0f}"),
        labels["pnl"]: top["unrealized_pnl"].apply(
            lambda x: f"+{currency_symbol}{x:,.0f}" if x >= 0 else f"-{currency_symbol}{abs(x):,.0f}"
        ),
        labels["pnl_pct"]: top["unrealized_pnl_pct"].apply(
            lambda x: f"+{x:.1f}%" if x >= 0 else f"{x:.1f}%"
        ),
        "_pnl_value": top["unrealized_pnl"]  # Hidden for styling
    })
    
    # Create DataTable
    table = dash_table.DataTable(
        id="top-holdings-table",
        columns=[
            {"name": labels["asset"], "id": labels["asset"]},
            {"name": labels["type"], "id": labels["type"]},
            {"name": labels["region"], "id": labels["region"]},
            {"name": labels["value"], "id": labels["value"]},
            {"name": labels["pnl"], "id": labels["pnl"]},
            {"name": labels["pnl_pct"], "id": labels["pnl_pct"]}
        ],
        data=display_df.to_dict("records"),
        sort_action="native",
        page_size=n,
        **TABLE_STYLE_BASE,
        style_data_conditional=[
            *DEFAULT_CONDITIONAL,
            {
                "if": {
                    "filter_query": "{_pnl_value} >= 0",
                    "column_id": [labels["pnl"], labels["pnl_pct"]]
                },
                "color": "#38a169"
            },
            {
                "if": {
                    "filter_query": "{_pnl_value} < 0",
                    "column_id": [labels["pnl"], labels["pnl_pct"]]
                },
                "color": "#c53030"
            }
        ]
    )
    
    return html.Div([
        html.H6(t("top_10_assets", lang), className="mb-3", style={"color": "#1a365d"}),
        table
    ])


def create_holdings_table(holdings_df: pd.DataFrame, view_mode: str = "value", lang: str = "en", currency_symbol: str = "€") -> html.Div:
    """
    Create full holdings table with search and filter.
    
    Args:
        holdings_df: Holdings DataFrame
        view_mode: 'value', 'cost', or 'pnl'
        lang: Language code ('en' or 'hu')
        currency_symbol: Currency symbol to display
    
    Returns:
        Dash table component
    """
    if holdings_df.empty:
        return html.Div(
            html.P(t("no_data", lang), className="text-muted text-center py-4"),
            className="border rounded"
        )
    
    # Column labels by language
    col_labels = {
        "en": {
            "asset": "Asset", "account": "Account", "type": "Type", "region": "Region",
            "sector": "Sector", "current_value": "Current Value", "cost_basis": "Cost Basis",
            "pnl": "P&L", "pnl_pct": "P&L %", "liquidity": "Liquidity"
        },
        "hu": {
            "asset": "Eszköz", "account": "Számla", "type": "Típus", "region": "Régió",
            "sector": "Szektor", "current_value": "Aktuális Érték", "cost_basis": "Beszerzési Érték",
            "pnl": "Profit/Veszt.", "pnl_pct": "Profit/Veszt. %", "liquidity": "Likviditás"
        }
    }
    labels = col_labels.get(lang, col_labels["en"])
    
    # Prepare data
    df = holdings_df.copy()
    df["unrealized_pnl"] = df["valuation_current"] - df["valuation_cost_basis"]
    df["unrealized_pnl_pct"] = (
        (df["valuation_current"] / df["valuation_cost_basis"] - 1) * 100
    )
    
    # Format columns
    display_df = pd.DataFrame({
        labels["asset"]: df["asset_name"],
        labels["account"]: df["account_id"],
        labels["type"]: df["asset_type"],
        labels["region"]: df["region"],
        labels["sector"]: df["sector"].fillna("-"),
        labels["current_value"]: df["valuation_current"].apply(lambda x: f"{currency_symbol}{x:,.0f}"),
        labels["cost_basis"]: df["valuation_cost_basis"].apply(lambda x: f"{currency_symbol}{x:,.0f}"),
        labels["pnl"]: df["unrealized_pnl"].apply(
            lambda x: f"+{currency_symbol}{x:,.0f}" if x >= 0 else f"-{currency_symbol}{abs(x):,.0f}"
        ),
        labels["pnl_pct"]: df["unrealized_pnl_pct"].apply(
            lambda x: f"+{x:.1f}%" if x >= 0 else f"{x:.1f}%"
        ),
        labels["liquidity"]: df["liquidity"] if "liquidity" in df.columns else df.get("liquidity_score", 0).apply(lambda x: f"{x:.0%}"),
        "_pnl_value": df["unrealized_pnl"],
        "_value": df["valuation_current"]
    })
    
    # Select columns based on view mode
    if view_mode == "cost":
        columns = [labels["asset"], labels["type"], labels["region"], labels["sector"], labels["cost_basis"], labels["current_value"]]
    elif view_mode == "pnl":
        columns = [labels["asset"], labels["type"], labels["region"], labels["pnl"], labels["pnl_pct"]]
    else:
        columns = [labels["asset"], labels["type"], labels["region"], labels["current_value"], labels["pnl_pct"], labels["liquidity"]]
    
    # Create DataTable
    table = dash_table.DataTable(
        id="holdings-table",
        columns=[{"name": c, "id": c} for c in columns],
        data=display_df.to_dict("records"),
        sort_action="native",
        filter_action="native",
        page_action="native",
        page_size=15,
        **TABLE_STYLE_BASE,
        style_data_conditional=[
            *DEFAULT_CONDITIONAL,
            {
                "if": {
                    "filter_query": "{_pnl_value} >= 0",
                    "column_id": [labels["pnl"], labels["pnl_pct"]]
                },
                "color": "#38a169"
            },
            {
                "if": {
                    "filter_query": "{_pnl_value} < 0",
                    "column_id": [labels["pnl"], labels["pnl_pct"]]
                },
                "color": "#c53030"
            }
        ]
    )
    
    return table


def create_transactions_table(transactions_df: pd.DataFrame, lang: str = "en", currency_symbol: str = "€") -> html.Div:
    """
    Create transactions table.
    
    Args:
        transactions_df: Transactions DataFrame
        lang: Language code ('en' or 'hu')
        currency_symbol: Currency symbol to display
    
    Returns:
        Dash table component
    """
    if transactions_df.empty:
        return html.Div(
            html.P(t("no_transactions", lang), className="text-muted text-center py-4"),
            className="border rounded"
        )
    
    # Column labels by language
    col_labels = {
        "en": {"date": "Date", "type": "Type", "asset": "Asset", "account": "Account", "amount": "Amount"},
        "hu": {"date": "Dátum", "type": "Típus", "asset": "Eszköz", "account": "Számla", "amount": "Összeg"}
    }
    labels = col_labels.get(lang, col_labels["en"])
    
    # Prepare data
    df = transactions_df.copy()
    df = df.sort_values("date", ascending=False)
    
    display_df = pd.DataFrame({
        labels["date"]: df["date"].dt.strftime("%Y-%m-%d"),
        labels["type"]: df["type"].str.capitalize(),
        labels["asset"]: df["asset_name"],
        labels["account"]: df["account_id"],
        labels["amount"]: df["amount"].apply(
            lambda x: f"+{currency_symbol}{x:,.0f}" if x >= 0 else f"-{currency_symbol}{abs(x):,.0f}"
        ),
        "_amount": df["amount"]
    })
    
    # Type colors
    type_colors = {
        "buy": "#3182ce",
        "sell": "#e53e3e",
        "dividend": "#38a169",
        "rent": "#48a9a6",
        "interest": "#d69e2e",
        "fee": "#718096"
    }
    
    # Create DataTable
    table = dash_table.DataTable(
        id="transactions-table",
        columns=[
            {"name": labels["date"], "id": labels["date"]},
            {"name": labels["type"], "id": labels["type"]},
            {"name": labels["asset"], "id": labels["asset"]},
            {"name": labels["account"], "id": labels["account"]},
            {"name": labels["amount"], "id": labels["amount"]}
        ],
        data=display_df.to_dict("records"),
        sort_action="native",
        filter_action="native",
        page_action="native",
        page_size=20,
        **TABLE_STYLE_BASE,
        style_data_conditional=[
            *DEFAULT_CONDITIONAL,
            {
                "if": {
                    "filter_query": "{_amount} >= 0",
                    "column_id": labels["amount"]
                },
                "color": "#38a169"
            },
            {
                "if": {
                    "filter_query": "{_amount} < 0",
                    "column_id": labels["amount"]
                },
                "color": "#c53030"
            }
        ]
    )
    
    return table


def create_quarterly_snapshot(
    total_value: float,
    ytd_return: float,
    allocation: pd.DataFrame,
    holdings_count: int,
    lang: str = "en",
    currency_symbol: str = "€"
) -> dbc.Card:
    """
    Create quarterly snapshot panel for reports.
    
    Args:
        total_value: Total portfolio value
        ytd_return: Year-to-date return percentage
        allocation: Asset allocation DataFrame
        holdings_count: Number of holdings
        lang: Language code ('en' or 'hu')
        currency_symbol: Currency symbol to display
    
    Returns:
        dbc.Card component
    """
    allocation_items = []
    for _, row in allocation.iterrows():
        allocation_items.append(
            html.Div([
                html.Span(row["asset_type"], className="me-2"),
                html.Span(
                    f"{currency_symbol}{row['value']:,.0f}",
                    className="fw-semibold"
                ),
                html.Span(
                    f" ({row['percentage']:.1f}%)",
                    className="text-muted"
                )
            ], className="mb-2")
        )
    
    # Labels by language
    snapshot_title = "Q4 2025 Pillanatkép" if lang == "hu" else "Q4 2025 Snapshot"
    
    return dbc.Card([
        dbc.CardHeader(
            html.H5(snapshot_title, className="mb-0"),
            className="bg-white border-bottom"
        ),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.P(t("total_portfolio_value", lang), className="text-muted mb-1 small"),
                        html.H4(f"{currency_symbol}{total_value:,.0f}", className="mb-0", style={"color": "#1a365d"})
                    ], className="mb-4"),
                    html.Div([
                        html.P("Idei Teljesítmény" if lang == "hu" else "YTD Performance", className="text-muted mb-1 small"),
                        html.H5(
                            f"{'+' if ytd_return >= 0 else ''}{ytd_return:.1f}%",
                            className="mb-0",
                            style={"color": "#38a169" if ytd_return >= 0 else "#c53030"}
                        )
                    ], className="mb-4"),
                    html.Div([
                        html.P("Befektetések Száma" if lang == "hu" else "Number of Holdings", className="text-muted mb-1 small"),
                        html.H5(f"{holdings_count}", className="mb-0", style={"color": "#1a365d"})
                    ])
                ], md=6),
                dbc.Col([
                    html.P(t("asset_allocation", lang), className="text-muted mb-2 small"),
                    html.Div(allocation_items)
                ], md=6)
            ])
        ])
    ], className="border-0 shadow-sm", style={"borderRadius": "8px"})

