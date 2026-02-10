"""
Layout components for SQN Trust dashboard.
"""

from datetime import datetime, timedelta

import dash_bootstrap_components as dbc
from dash import html, dcc

from services.translations import t


def create_header(client_name: str) -> dbc.Navbar:
    """
    Create the dashboard header with branding, client name, and language toggle.
    
    Args:
        client_name: Client name to display
    
    Returns:
        dbc.Navbar component
    """
    return dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4(
                            "SQN Trust",
                            className="mb-0 me-3 fw-bold",
                            style={"color": "#1a365d", "letterSpacing": "-0.5px"}
                        ),
                        html.Span(
                            "|",
                            className="text-muted me-3",
                            style={"fontSize": "1.5rem", "fontWeight": "200"}
                        ),
                        html.Span(
                            id="header-subtitle",
                            className="text-muted",
                            style={"fontSize": "0.9rem"}
                        )
                    ], className="d-flex align-items-center")
                ], width="auto"),
                dbc.Col([
                    html.Div([
                        # Language toggle
                        dbc.ButtonGroup([
                            dbc.Button(
                                "EN",
                                id="lang-en",
                                color="secondary",
                                size="sm",
                                outline=False,
                                className="px-2"
                            ),
                            dbc.Button(
                                "HU",
                                id="lang-hu",
                                color="outline-secondary",
                                size="sm",
                                className="px-2"
                            )
                        ], size="sm", className="me-4"),
                        html.Span(
                            client_name,
                            className="fw-semibold",
                            style={"color": "#2d5a87", "fontSize": "1.1rem"}
                        )
                    ], className="d-flex align-items-center justify-content-end")
                ], className="ms-auto")
            ], align="center", className="w-100")
        ], fluid=True),
        color="white",
        className="border-bottom shadow-sm py-3",
        style={"backgroundColor": "#ffffff"}
    )


def create_filter_bar() -> dbc.Card:
    """
    Create the global filter bar.
    
    Returns:
        dbc.Card component with filters
    """
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                # Asset type filter
                dbc.Col([
                    html.Label(
                        "Asset Type",
                        className="form-label small text-muted mb-1"
                    ),
                    dcc.Dropdown(
                        id="asset-type-filter",
                        placeholder="All Assets",
                        value="all",
                        clearable=False,
                        className="dash-dropdown"
                    )
                ], md=3, sm=6, xs=12, className="mb-2 mb-md-0"),
                
                # Date range filter
                dbc.Col([
                    html.Label(
                        "Date Range",
                        className="form-label small text-muted mb-1"
                    ),
                    dcc.DatePickerRange(
                        id="date-range-filter",
                        start_date=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
                        end_date=datetime.now().strftime("%Y-%m-%d"),
                        display_format="MMM D, YYYY",
                        className="dash-datepicker"
                    )
                ], md=3, sm=6, xs=12, className="mb-2 mb-md-0"),
                
                # Currency toggle
                dbc.Col([
                    html.Label(
                        "Currency",
                        className="form-label small text-muted mb-1"
                    ),
                    dbc.RadioItems(
                        id="currency-toggle",
                        options=[
                            {"label": "EUR", "value": "EUR"},
                            {"label": "USD", "value": "USD"},
                            {"label": "HUF", "value": "HUF"}
                        ],
                        value="EUR",
                        inline=True,
                        className="btn-group",
                        inputClassName="btn-check",
                        labelClassName="btn btn-outline-secondary btn-sm",
                        labelCheckedClassName="btn btn-secondary btn-sm"
                    )
                ], md=3, sm=6, xs=12, className="mb-2 mb-md-0"),
                
                # Period quick selector
                dbc.Col([
                    html.Label(
                        "Quick Period",
                        className="form-label small text-muted mb-1"
                    ),
                    dbc.ButtonGroup([
                        dbc.Button("1M", id="period-1m", color="outline-secondary", size="sm"),
                        dbc.Button("3M", id="period-3m", color="outline-secondary", size="sm"),
                        dbc.Button("6M", id="period-6m", color="outline-secondary", size="sm"),
                        dbc.Button("1Y", id="period-1y", color="secondary", size="sm"),
                        dbc.Button("All", id="period-all", color="outline-secondary", size="sm")
                    ], size="sm")
                ], md=3, sm=12, xs=12, className="d-flex flex-column")
            ], align="end")
        ], className="py-2")
    ], className="border-0 shadow-sm mb-4", style={"borderRadius": "8px"})


def create_tabs(lang: str = "en") -> dbc.Tabs:
    """
    Create the main navigation tabs.
    
    Args:
        lang: Language code ('en' or 'hu')
    
    Returns:
        dbc.Tabs component
    """
    return dbc.Tabs(
        id="main-tabs",
        active_tab="summary",
        className="nav-tabs-custom mb-4",
        children=[
            dbc.Tab(label=t("tab_summary", lang), tab_id="summary", id="tab-summary", className="nav-tab-custom"),
            dbc.Tab(label=t("tab_assets", lang), tab_id="assets", id="tab-assets", className="nav-tab-custom"),
            dbc.Tab(label=t("tab_ownership", lang), tab_id="ownership", id="tab-ownership", className="nav-tab-custom"),
            dbc.Tab(label=t("tab_map", lang), tab_id="map", id="tab-map", className="nav-tab-custom"),
            dbc.Tab(label=t("tab_diversity", lang), tab_id="diversity", id="tab-diversity", className="nav-tab-custom"),
            dbc.Tab(label=t("tab_insights", lang), tab_id="insights", id="tab-insights", className="nav-tab-custom"),
            dbc.Tab(label=t("tab_reports", lang), tab_id="reports", id="tab-reports", className="nav-tab-custom"),
            dbc.Tab(label=t("tab_about", lang), tab_id="about", id="tab-about", className="nav-tab-custom")
        ]
    )


def create_insights_panel(insights: list) -> dbc.Card:
    """
    Create insights panel with auto-generated bullets.
    
    Args:
        insights: List of insight dictionaries with 'title' and 'text'
    
    Returns:
        dbc.Card component
    """
    insight_items = []
    for insight in insights:
        insight_items.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6(
                            insight["title"],
                            className="mb-2",
                            style={"color": "#2d5a87"}
                        ),
                        html.P(
                            insight["text"],
                            className="mb-0 small text-muted"
                        )
                    ], className="p-3")
                ], className="h-100 border-0 bg-light", style={"borderRadius": "6px"})
            ], md=4, sm=6, xs=12, className="mb-3")
        )
    
    return dbc.Card([
        dbc.CardHeader([
            html.H5("Portfolio Insights", className="mb-0"),
            html.Small("Auto-generated analysis based on your portfolio", className="text-muted")
        ], className="bg-white border-bottom d-flex justify-content-between align-items-center"),
        dbc.CardBody([
            dbc.Row(insight_items)
        ])
    ], className="border-0 shadow-sm", style={"borderRadius": "8px"})


def create_empty_state(message: str = "No data available") -> html.Div:
    """
    Create an empty state component.
    
    Args:
        message: Message to display
    
    Returns:
        html.Div component
    """
    return html.Div([
        html.Div([
            html.I(className="bi bi-inbox fs-1 text-muted mb-3"),
            html.P(message, className="text-muted mb-0")
        ], className="text-center py-5")
    ], className="border rounded bg-light")


def create_section_header(title: str, subtitle: str = None) -> html.Div:
    """
    Create a section header.
    
    Args:
        title: Section title
        subtitle: Optional subtitle
    
    Returns:
        html.Div component
    """
    elements = [
        html.H5(title, className="mb-1", style={"color": "#1a365d"})
    ]
    
    if subtitle:
        elements.append(
            html.Small(subtitle, className="text-muted")
        )
    
    return html.Div(elements, className="mb-3")


def create_metric_card(
    title: str,
    value: str,
    subtitle: str = None,
    color: str = "primary"
) -> dbc.Card:
    """
    Create a small metric card.
    
    Args:
        title: Card title
        value: Main value
        subtitle: Optional subtitle
        color: Bootstrap color
    
    Returns:
        dbc.Card component
    """
    return dbc.Card([
        dbc.CardBody([
            html.P(
                title,
                className="text-muted mb-1 small text-uppercase",
                style={"letterSpacing": "0.5px"}
            ),
            html.H4(value, className="mb-0", style={"color": "#1a365d"}),
            html.Small(subtitle, className="text-muted") if subtitle else None
        ], className="p-3")
    ], className="border-0 shadow-sm h-100", style={"borderRadius": "8px"})


# Custom CSS styles
CUSTOM_CSS = """
/* SQN Trust Custom Styles */

body {
    background-color: #f8fafc;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Hide filter bar on mobile */
@media (max-width: 768px) {
    .mobile-hide-filter {
        display: none !important;
    }
    
    /* Horizontal scrollable tabs on mobile */
    .nav-tabs-custom {
        display: flex;
        flex-wrap: nowrap !important;
        overflow-x: auto;
        overflow-y: hidden;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: thin;
    }
    
    .nav-tabs-custom .nav-item {
        flex: 0 0 auto;
    }
    
    .nav-tabs-custom .nav-link {
        white-space: nowrap;
    }
}

/* Dropdown styling */
.dash-dropdown .Select-control {
    border-radius: 6px;
    border-color: #e2e8f0;
}

.dash-dropdown .Select-control:hover {
    border-color: #cbd5e0;
}

/* Tab styling */
.nav-tabs-custom {
    border-bottom: 2px solid #e2e8f0;
}

.nav-tabs-custom .nav-link {
    color: #718096;
    border: none;
    padding: 0.75rem 1.25rem;
    font-weight: 500;
    transition: all 0.2s ease;
}

.nav-tabs-custom .nav-link:hover {
    color: #1a365d;
    border: none;
}

.nav-tabs-custom .nav-link.active {
    color: #1a365d;
    border: none;
    border-bottom: 2px solid #1a365d;
    margin-bottom: -2px;
    background: transparent;
}

/* Card hover effects */
.card {
    transition: box-shadow 0.2s ease;
}

.card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
}

/* Button group styling */
.btn-group .btn-outline-secondary {
    border-color: #e2e8f0;
}

.btn-group .btn-outline-secondary:hover {
    background-color: #f7fafc;
    border-color: #cbd5e0;
}

/* Date picker styling */
.DateInput_input {
    font-size: 0.875rem;
    padding: 6px 10px;
    border-radius: 6px;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
    background: #cbd5e0;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #a0aec0;
}
"""

