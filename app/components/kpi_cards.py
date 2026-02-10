"""
KPI Card components for SQN Trust dashboard.
"""

import dash_bootstrap_components as dbc
from dash import html


def create_kpi_card(
    title: str,
    value: str,
    subtitle: str = "",
    icon: str = None,
    color: str = "primary",
    tooltip: str = None,
    trend: str = None,
    trend_direction: str = None
) -> dbc.Card:
    """
    Create a KPI card component.
    
    Args:
        title: Card title
        value: Main value to display
        subtitle: Optional subtitle
        icon: Optional icon class
        color: Bootstrap color class
        tooltip: Optional tooltip text
        trend: Optional trend value (e.g., "+5.2%")
        trend_direction: 'up', 'down', or 'neutral'
    
    Returns:
        dbc.Card component
    """
    # Determine trend color and icon
    trend_color = "text-muted"
    trend_icon = ""
    if trend_direction == "up":
        trend_color = "text-success"
        trend_icon = "↑ "
    elif trend_direction == "down":
        trend_color = "text-danger"
        trend_icon = "↓ "
    
    card_content = [
        html.Div(
            [
                html.P(
                    title,
                    className="text-muted mb-1 text-uppercase",
                    style={"fontSize": "0.75rem", "letterSpacing": "0.5px", "fontWeight": "500"}
                ),
                html.H3(
                    value,
                    className="mb-0 fw-semibold",
                    style={"color": "#1a365d", "fontSize": "1.5rem"}
                ),
            ],
            className="d-flex flex-column"
        )
    ]
    
    if subtitle:
        card_content.append(
            html.Small(subtitle, className="text-muted")
        )
    
    if trend:
        card_content.append(
            html.Div(
                html.Small(
                    f"{trend_icon}{trend}",
                    className=trend_color,
                    style={"fontWeight": "500"}
                ),
                className="mt-2"
            )
        )
    
    card_body = dbc.CardBody(
        card_content,
        className="p-3"
    )
    
    card = dbc.Card(
        card_body,
        className="h-100 border-0 shadow-sm",
        style={
            "borderRadius": "8px",
            "backgroundColor": "#ffffff",
            "borderLeft": f"3px solid var(--bs-{color})"
        }
    )
    
    if tooltip:
        card = html.Div(
            [
                card,
                dbc.Tooltip(tooltip, target=f"kpi-{title.replace(' ', '-').lower()}")
            ],
            id=f"kpi-{title.replace(' ', '-').lower()}"
        )
    
    return card


def create_kpi_row(kpis: list) -> dbc.Row:
    """
    Create a row of KPI cards.
    
    Args:
        kpis: List of KPI card configurations
    
    Returns:
        dbc.Row with KPI cards
    """
    cols = []
    for kpi in kpis:
        cols.append(
            dbc.Col(
                create_kpi_card(**kpi),
                xs=6, sm=6, md=4, lg=True,
                className="mb-3"
            )
        )
    
    return dbc.Row(cols, className="g-3")


def format_currency(value: float, currency: str = "EUR", decimals: int = 0) -> str:
    """Format value as currency string."""
    symbols = {"EUR": "€", "USD": "$", "HUF": "Ft", "GBP": "£"}
    symbol = symbols.get(currency, currency)
    
    if abs(value) >= 1_000_000:
        formatted = f"{value / 1_000_000:.1f}M"
    elif abs(value) >= 1_000:
        formatted = f"{value / 1_000:.0f}K"
    else:
        formatted = f"{value:,.{decimals}f}"
    
    return f"{symbol}{formatted}"


def format_percentage(value: float, decimals: int = 1, show_sign: bool = False) -> str:
    """Format value as percentage string."""
    sign = "+" if show_sign and value > 0 else ""
    return f"{sign}{value:.{decimals}f}%"

