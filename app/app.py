#!/usr/bin/env python3
"""
SQN Trust Portfolio Dashboard
A premium wealth management dashboard for portfolio visualization and analysis.
"""

import io
from datetime import datetime, timedelta

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State
import pandas as pd

# Import services
from services.data_loader import (
    load_client, load_accounts, load_holdings, load_transactions, load_nav,
    load_ownership, load_real_estate_locations, get_account_options, get_asset_type_options, convert_currency
)
from services.filters import filter_holdings, filter_transactions, filter_nav, parse_date_range
from services.metrics import (
    calculate_total_value, calculate_unrealized_pnl, calculate_returns_from_nav,
    calculate_ytd_return, calculate_volatility, calculate_max_drawdown,
    calculate_asset_allocation, calculate_region_allocation, calculate_sector_allocation,
    get_top_holdings, calculate_concentration, calculate_liquidity_score,
    calculate_cash_percentage, generate_insights,
    calculate_cashflow_summary, calculate_income_summary
)
from services.translations import t

# Import components
from components.layout import (
    create_header, create_filter_bar, create_tabs, create_insights_panel,
    create_empty_state, create_section_header, create_metric_card, CUSTOM_CSS
)
from components.kpi_cards import create_kpi_row, format_currency, format_percentage
from components.charts import (
    create_allocation_donut, create_nav_line_chart, create_region_bar_chart,
    create_sector_bar_chart, create_cashflow_chart, create_property_type_donut,
    create_geography_bar, create_account_breakdown_donut
)
from components.tables import (
    create_top_holdings_table, create_holdings_table, create_transactions_table,
    create_quarterly_snapshot
)

# Initialize app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css",
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    ],
    suppress_callback_exceptions=True,
    title="SQN | Portfolio Dashboard"
)

# Load initial data
client = load_client()

# App layout
# Inject custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
''' + CUSTOM_CSS + '''
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div([
    # Header
    create_header(client["name"]),
    
    # Main container
    dbc.Container([
        # Filter bar
        html.Div(create_filter_bar(), className="mt-4 mobile-hide-filter"),
        
        # Tabs
        create_tabs(),
        
        # Tab content
        html.Div(id="tab-content")
        
    ], fluid=True, className="px-4 pb-5"),
    
    # Download components (hidden)
    dcc.Download(id="download-holdings"),
    
    # Store for filtered data state
    dcc.Store(id="filtered-data-store"),
    
    # Store for language state
    dcc.Store(id="language-store", data="en")
    
], style={"minHeight": "100vh", "backgroundColor": "#f8fafc"})


# ==================== CALLBACKS ====================

@callback(
    Output("asset-type-filter", "options"),
    Input("asset-type-filter", "id")  # Dummy input for initial load
)
def populate_filter_options(_):
    """Populate filter dropdown options on load."""
    return get_asset_type_options()


# Language toggle callbacks
@callback(
    Output("language-store", "data"),
    Output("lang-en", "color"),
    Output("lang-en", "outline"),
    Output("lang-hu", "color"),
    Output("lang-hu", "outline"),
    Input("lang-en", "n_clicks"),
    Input("lang-hu", "n_clicks"),
    State("language-store", "data"),
    prevent_initial_call=True
)
def toggle_language(en_clicks, hu_clicks, current_lang):
    """Toggle between English and Hungarian."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "lang-en":
        return "en", "secondary", False, "outline-secondary", True
    else:
        return "hu", "outline-secondary", True, "secondary", False


@callback(
    Output("header-subtitle", "children"),
    Input("language-store", "data")
)
def update_header_subtitle(lang):
    """Update header subtitle based on language."""
    return t("subtitle", lang)


@callback(
    Output("tab-summary", "label"),
    Output("tab-assets", "label"),
    Output("tab-ownership", "label"),
    Output("tab-map", "label"),
    Output("tab-diversity", "label"),
    Output("tab-insights", "label"),
    Output("tab-reports", "label"),
    Output("tab-about", "label"),
    Input("language-store", "data")
)
def update_tab_labels(lang):
    """Update tab labels based on language."""
    if lang is None:
        lang = "en"
    return (
        t("tab_summary", lang),
        t("tab_assets", lang),
        t("tab_ownership", lang),
        t("tab_map", lang),
        t("tab_diversity", lang),
        t("tab_insights", lang),
        t("tab_reports", lang),
        t("tab_about", lang)
    )


@callback(
    Output("date-range-filter", "start_date"),
    Output("date-range-filter", "end_date"),
    Output("period-1m", "color"),
    Output("period-3m", "color"),
    Output("period-6m", "color"),
    Output("period-1y", "color"),
    Output("period-all", "color"),
    Input("period-1m", "n_clicks"),
    Input("period-3m", "n_clicks"),
    Input("period-6m", "n_clicks"),
    Input("period-1y", "n_clicks"),
    Input("period-all", "n_clicks"),
    prevent_initial_call=True
)
def update_date_range_from_period(n1m, n3m, n6m, n1y, nall):
    """Update date range when period buttons are clicked."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    period_map = {
        "period-1m": "1M",
        "period-3m": "3M",
        "period-6m": "6M",
        "period-1y": "1Y",
        "period-all": "ALL"
    }
    
    period = period_map.get(button_id, "1Y")
    start_date, end_date = parse_date_range(period)
    
    # Update button colors
    colors = {
        "period-1m": "outline-secondary",
        "period-3m": "outline-secondary",
        "period-6m": "outline-secondary",
        "period-1y": "outline-secondary",
        "period-all": "outline-secondary"
    }
    colors[button_id] = "secondary"
    
    return (
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d"),
        colors["period-1m"],
        colors["period-3m"],
        colors["period-6m"],
        colors["period-1y"],
        colors["period-all"]
    )


@callback(
    Output("tab-content", "children"),
    Input("main-tabs", "active_tab"),
    Input("date-range-filter", "start_date"),
    Input("date-range-filter", "end_date"),
    Input("currency-toggle", "value"),
    Input("asset-type-filter", "value"),
    Input("language-store", "data")
)
def render_tab_content(active_tab, start_date, end_date, currency, asset_type, lang):
    """Render the content for the active tab."""
    if lang is None:
        lang = "en"
    
    # Load data
    holdings = load_holdings()
    transactions = load_transactions()
    nav = load_nav()
    accounts = load_accounts()
    
    # Apply filters
    date_range = (start_date, end_date) if start_date and end_date else None
    
    filtered_holdings = filter_holdings(holdings, None, asset_type, date_range)
    filtered_transactions = filter_transactions(transactions, None, None, date_range)
    filtered_nav = filter_nav(nav, None, date_range)
    
    # Currency conversion (simplified)
    # Conversion rates from EUR
    conversion_rates = {
        "EUR": 1.0,
        "USD": 1.09,  # EUR to USD
        "HUF": 395.0  # EUR to HUF
    }
    currency_symbols = {
        "EUR": "€",
        "USD": "$",
        "HUF": "Ft "
    }
    
    if currency != "EUR":
        conversion_rate = conversion_rates.get(currency, 1.0)
        filtered_holdings = filtered_holdings.copy()
        filtered_holdings["valuation_current"] = filtered_holdings["valuation_current"] * conversion_rate
        filtered_holdings["valuation_cost_basis"] = filtered_holdings["valuation_cost_basis"] * conversion_rate
        filtered_nav = filtered_nav.copy()
        filtered_nav["value"] = filtered_nav["value"] * conversion_rate
    
    currency_symbol = currency_symbols.get(currency, "€")
    
    # Render based on active tab
    if active_tab == "summary":
        return render_summary_tab(filtered_holdings, filtered_nav, accounts, currency_symbol, lang)
    elif active_tab == "assets":
        return render_assets_tab(filtered_holdings, accounts, currency_symbol, asset_type, lang)
    elif active_tab == "ownership":
        return render_ownership_tab(currency_symbol, lang)
    elif active_tab == "map":
        return render_map_tab(filtered_holdings, currency_symbol, lang)
    elif active_tab == "diversity":
        return render_diversity_tab(filtered_holdings, currency_symbol, lang)
    elif active_tab == "insights":
        return render_insights_tab(filtered_holdings, filtered_nav, lang, currency_symbol)
    elif active_tab == "reports":
        return render_reports_tab(filtered_holdings, currency_symbol, lang)
    elif active_tab == "about":
        return render_about_tab(lang)
    
    return html.Div("Select a tab")


def render_summary_tab(holdings, nav, accounts, currency_symbol, lang="en"):
    """Render the Summary tab content."""
    
    if holdings.empty:
        return create_empty_state(t("no_assets", lang))
    
    # Calculate metrics
    total_value = calculate_total_value(holdings)
    pnl_abs, pnl_pct = calculate_unrealized_pnl(holdings)
    
    returns_1y = calculate_returns_from_nav(nav, 365)
    ytd_return = calculate_ytd_return(nav)
    volatility = calculate_volatility(nav)
    cash_pct = calculate_cash_percentage(holdings)
    
    # Asset allocation
    allocation = calculate_asset_allocation(holdings)
    region_allocation = calculate_region_allocation(holdings)
    sector_allocation = calculate_sector_allocation(holdings)
    
    # Concentration
    concentration = calculate_concentration(holdings, 3)
    
    return html.Div([
        # Row 1: KPI Cards
        create_kpi_row([
            {
                "title": t("total_portfolio_value", lang),
                "value": f"{currency_symbol}{total_value:,.0f}",
                "color": "primary",
                "tooltip": t("tooltip_portfolio_value", lang)
            },
            {
                "title": t("1y_return", lang),
                "value": format_percentage(returns_1y["return_pct"], show_sign=True),
                "color": "success" if returns_1y["return_pct"] >= 0 else "danger",
                "trend_direction": "up" if returns_1y["return_pct"] >= 0 else "down",
                "tooltip": t("tooltip_1y_return", lang)
            },
            {
                "title": t("ytd_return", lang),
                "value": format_percentage(ytd_return, show_sign=True),
                "color": "success" if ytd_return >= 0 else "danger",
                "trend_direction": "up" if ytd_return >= 0 else "down",
                "tooltip": t("tooltip_ytd_return", lang)
            },
            {
                "title": t("volatility", lang),
                "value": format_percentage(volatility),
                "color": "warning",
                "tooltip": t("tooltip_volatility", lang)
            }
        ]),
        
        html.Div(className="mb-4"),
        
        # Row 2: Allocation and NAV chart
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H6(t("asset_allocation", lang), className="mb-0"),
                        className="bg-white border-bottom"
                    ),
                    dbc.CardBody([
                        dcc.Graph(
                            figure=create_allocation_donut(allocation),
                            config={"displayModeBar": False}
                        )
                    ])
                ], className="border-0 shadow-sm h-100", style={"borderRadius": "8px"})
            ], lg=5, md=12, className="mb-4"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H6(t("portfolio_value_over_time", lang), className="mb-0 d-inline"),
                    ], className="bg-white border-bottom"),
                    dbc.CardBody([
                        dcc.Graph(
                            id="nav-chart",
                            figure=create_nav_line_chart(nav),
                            config={"displayModeBar": False}
                        )
                    ])
                ], className="border-0 shadow-sm h-100", style={"borderRadius": "8px"})
            ], lg=7, md=12, className="mb-4")
        ]),
        
        # Row 3: Top assets
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        create_top_holdings_table(holdings, lang, currency_symbol)
                    ])
                ], className="border-0 shadow-sm h-100", style={"borderRadius": "8px"})
            ], lg=12, md=12, className="mb-4")
        ])
    ])


def render_assets_tab(holdings, accounts, currency_symbol, current_asset_type, lang="en"):
    """Render the Assets tab content."""
    
    if holdings.empty:
        return create_empty_state(t("no_assets", lang))
    
    # Determine which breakdown to show
    if current_asset_type == "Shares" or (current_asset_type == "all" and 
        holdings[holdings["asset_type"] == "Shares"]["valuation_current"].sum() > 
        holdings["valuation_current"].sum() * 0.5):
        # Show sector and region for shares
        breakdown_content = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            figure=create_sector_bar_chart(calculate_sector_allocation(holdings)),
                            config={"displayModeBar": False}
                        )
                    ])
                ], className="border-0 shadow-sm h-100", style={"borderRadius": "8px"})
            ], md=6, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            figure=create_region_bar_chart(calculate_region_allocation(holdings)),
                            config={"displayModeBar": False}
                        )
                    ])
                ], className="border-0 shadow-sm h-100", style={"borderRadius": "8px"})
            ], md=6, className="mb-4")
        ])
    elif current_asset_type == "RealEstate":
        # Show property type and geography
        breakdown_content = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            figure=create_property_type_donut(holdings),
                            config={"displayModeBar": False}
                        )
                    ])
                ], className="border-0 shadow-sm h-100", style={"borderRadius": "8px"})
            ], md=6, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            figure=create_geography_bar(holdings),
                            config={"displayModeBar": False}
                        )
                    ])
                ], className="border-0 shadow-sm h-100", style={"borderRadius": "8px"})
            ], md=6, className="mb-4")
        ])
    elif current_asset_type == "Liquid":
        # Show by account
        breakdown_content = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            figure=create_account_breakdown_donut(holdings, accounts),
                            config={"displayModeBar": False}
                        )
                    ])
                ], className="border-0 shadow-sm h-100", style={"borderRadius": "8px"})
            ], md=6, className="mb-4")
        ])
    else:
        # Default: show sector and region
        breakdown_content = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            figure=create_sector_bar_chart(calculate_sector_allocation(holdings)),
                            config={"displayModeBar": False}
                        )
                    ])
                ], className="border-0 shadow-sm h-100", style={"borderRadius": "8px"})
            ], md=6, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            figure=create_region_bar_chart(calculate_region_allocation(holdings)),
                            config={"displayModeBar": False}
                        )
                    ])
                ], className="border-0 shadow-sm h-100", style={"borderRadius": "8px"})
            ], md=6, className="mb-4")
        ])
    
    return html.Div([
        # Breakdown charts
        breakdown_content,
        
        # Holdings table
        dbc.Card([
            dbc.CardHeader(
                html.H6(t("all_assets", lang), className="mb-0"),
                className="bg-white border-bottom"
            ),
            dbc.CardBody([
                create_holdings_table(holdings, "value", lang, currency_symbol)
            ])
        ], className="border-0 shadow-sm", style={"borderRadius": "8px"})
    ])


def render_map_tab(holdings, currency_symbol, lang="en"):
    """Render the Map tab with real estate properties on an interactive map."""
    import plotly.graph_objects as go
    
    # Filter for real estate only
    real_estate = holdings[holdings["asset_type"] == "RealEstate"].copy()
    
    if real_estate.empty:
        return create_empty_state(t("no_data", lang) if lang == "en" else "Nincs ingatlan adat")
    
    # Load real estate locations data
    locations = load_real_estate_locations()
    
    # Create location dataframe
    if locations:
        location_df = pd.DataFrame(locations)
        # Match by name
        if "name" in location_df.columns:
            merged = real_estate.merge(location_df, left_on="asset_name", right_on="name", how="left", suffixes=("", "_loc"))
        else:
            merged = real_estate.copy()
            merged["lat"] = 47.4979
            merged["lon"] = 19.0402
    else:
        merged = real_estate.copy()
        merged["lat"] = 47.4979
        merged["lon"] = 19.0402
    
    # Fill missing coordinates with defaults
    merged["lat"] = merged["lat"].fillna(47.4979)
    merged["lon"] = merged["lon"].fillna(19.0402)
    
    # Create hover text with property details
    hover_texts = []
    for _, row in merged.iterrows():
        size_info = f"<br>Size: {row.get('size_sqm', 'N/A')} m²" if 'size_sqm' in row and pd.notna(row.get('size_sqm')) else ""
        prop_type = row.get('property_type', 'Property')
        city = row.get('city', row.get('address', 'N/A'))
        
        hover_texts.append(
            f"<b>{row['asset_name']}</b><br>"
            f"Type: {prop_type}<br>"
            f"Value: {currency_symbol}{row['valuation_current']:,.0f}<br>"
            f"Location: {city}"
            f"{size_info}"
        )
    
    # Scale marker sizes based on value
    max_value = merged["valuation_current"].max()
    min_size = 15
    max_size = 40
    
    marker_sizes = merged["valuation_current"].apply(
        lambda x: min_size + (max_size - min_size) * (x / max_value) if max_value > 0 else min_size
    )
    
    # Color based on property type
    sector_colors = {
        "Residential": "#38a169",
        "Commercial": "#3182ce",
        "Industrial": "#d69e2e",
        "Mixed-Use": "#805ad5",
        "Retail": "#e53e3e"
    }
    
    marker_colors = merged["property_type"].apply(
        lambda x: sector_colors.get(x, "#1a365d") if pd.notna(x) else "#1a365d"
    )
    
    # Create map using Scattergeo (no token needed)
    fig = go.Figure()
    
    fig.add_trace(go.Scattergeo(
        lat=merged["lat"],
        lon=merged["lon"],
        mode='markers',
        marker=dict(
            size=marker_sizes,
            color=marker_colors.tolist(),
            opacity=0.85,
            line=dict(width=1, color="white")
        ),
        text=hover_texts,
        hovertemplate="%{text}<extra></extra>",
    ))
    
    # Center map on Europe
    fig.update_layout(
        geo=dict(
            scope='europe',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
            showcoastlines=True,
            coastlinecolor='rgb(204, 204, 204)',
            showframe=False,
            projection_type='natural earth',
            center=dict(lat=48.5, lon=15),
            bgcolor="rgba(0,0,0,0)"
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        height=500,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)"
    )
    
    # Calculate summary stats
    total_properties = len(real_estate)
    total_value = real_estate["valuation_current"].sum()
    avg_value = real_estate["valuation_current"].mean()
    
    # Create property cards
    property_cards = []
    for _, row in merged.head(6).iterrows():
        prop_type = row.get('property_type', 'Property')
        city = row.get('city', row.get('address', 'N/A'))
        size = row.get('size_sqm', None)
        
        property_cards.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6(row["asset_name"], className="mb-2", style={"color": "#1a365d"}),
                        html.P([
                            html.Span(prop_type, className="badge bg-primary me-2"),
                            html.Span(city, className="text-muted small")
                        ], className="mb-2"),
                        html.Div([
                            html.Span(f"{currency_symbol}{row['valuation_current']:,.0f}", 
                                     className="fw-bold", style={"fontSize": "1.1rem"}),
                            html.Span(f" • {size:,} m²" if size and pd.notna(size) else "", className="text-muted ms-2")
                        ])
                    ], className="py-3")
                ], className="border-0 shadow-sm h-100", style={"borderRadius": "8px"})
            ], md=4, className="mb-3")
        )
    
    return html.Div([
        # Header
        dbc.Row([
            dbc.Col([
                html.H4(t("real_estate_map", lang), className="mb-1", style={"color": "#1a365d"}),
                html.P(t("map_subtitle", lang), className="text-muted mb-4")
            ])
        ]),
        
        # Summary cards
        dbc.Row([
            # Total Real Estate Value - First on mobile
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.P(t("total_real_estate_value", lang), className="text-muted mb-1 small"),
                        html.H4(f"{currency_symbol}{total_value:,.0f}", className="mb-0", style={"color": "#38a169"})
                    ])
                ], className="border-0 shadow-sm text-center", style={"borderRadius": "8px"})
            ], xs=12, sm=4, md=4, className="mb-3", style={"order": "0"}),
            # Total Properties - Second row on mobile
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.P(t("total_properties", lang), className="text-muted mb-1 small"),
                        html.H4(f"{total_properties}", className="mb-0", style={"color": "#1a365d"})
                    ])
                ], className="border-0 shadow-sm text-center", style={"borderRadius": "8px"})
            ], xs=6, sm=4, md=4, className="mb-3", style={"order": "1"}),
            # Avg. Value - Second row on mobile
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.P("Avg. Value" if lang == "en" else "Átl. Érték", className="text-muted mb-1 small"),
                        html.H4(f"{currency_symbol}{avg_value:,.0f}", className="mb-0", style={"color": "#3182ce"})
                    ])
                ], className="border-0 shadow-sm text-center", style={"borderRadius": "8px"})
            ], xs=6, sm=4, md=4, className="mb-3", style={"order": "2"}),
        ], className="mb-4"),
        
        # Map
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig, config={"displayModeBar": False, "scrollZoom": True})
                    ], className="p-0")
                ], className="border-0 shadow-sm", style={"borderRadius": "8px", "overflow": "hidden"})
            ])
        ], className="mb-4"),
        
        # Property list
        dbc.Row([
            dbc.Col([
                html.H5("Properties" if lang == "en" else "Ingatlanok", className="mb-3", style={"color": "#1a365d"})
            ])
        ]),
        dbc.Row(property_cards),
        
        # Legend
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Span("● ", style={"color": "#38a169", "fontSize": "1rem"}),
                    html.Span("Residential" if lang == "en" else "Lakóingatlan", className="me-3 small"),
                    html.Span("● ", style={"color": "#3182ce", "fontSize": "1rem"}),
                    html.Span("Commercial" if lang == "en" else "Kereskedelmi", className="me-3 small"),
                    html.Span("● ", style={"color": "#d69e2e", "fontSize": "1rem"}),
                    html.Span("Industrial" if lang == "en" else "Ipari", className="me-3 small"),
                    html.Span("● ", style={"color": "#805ad5", "fontSize": "1rem"}),
                    html.Span("Mixed" if lang == "en" else "Vegyes", className="small")
                ], className="text-center text-muted mt-3")
            ])
        ])
    ])


def render_diversity_tab(holdings, currency_symbol, lang="en"):
    """Render the Diversity tab content with risk, sector, volatility, and geographic charts."""
    
    if holdings.empty:
        return create_empty_state(t("no_assets", lang))
    
    # Calculate diversity metrics
    region_allocation = calculate_region_allocation(holdings)
    sector_allocation = calculate_sector_allocation(holdings)
    
    # Risk distribution (if risk_level exists)
    risk_data = None
    if "risk_level" in holdings.columns:
        risk_grouped = holdings.groupby("risk_level")["valuation_current"].sum().reset_index()
        risk_grouped.columns = ["risk_level", "value"]
        risk_grouped["percentage"] = (risk_grouped["value"] / risk_grouped["value"].sum() * 100).round(1)
        risk_data = risk_grouped
    
    # Volatility breakdown (if volatility exists)
    volatility_data = None
    if "volatility" in holdings.columns:
        # Group volatility into buckets
        def volatility_bucket(v):
            if v < 0.10:
                return "Low (<10%)"
            elif v < 0.25:
                return "Medium (10-25%)"
            else:
                return "High (>25%)"
        
        holdings_vol = holdings.copy()
        holdings_vol["vol_bucket"] = holdings_vol["volatility"].apply(volatility_bucket)
        volatility_grouped = holdings_vol.groupby("vol_bucket")["valuation_current"].sum().reset_index()
        volatility_grouped.columns = ["volatility_bucket", "value"]
        volatility_grouped["percentage"] = (volatility_grouped["value"] / volatility_grouped["value"].sum() * 100).round(1)
        volatility_data = volatility_grouped
    
    # Country distribution
    country_data = None
    if "country" in holdings.columns:
        country_grouped = holdings[holdings["country"].notna()].groupby("country")["valuation_current"].sum().reset_index()
        country_grouped.columns = ["country", "value"]
        country_grouped = country_grouped.sort_values("value", ascending=False)
        country_grouped["percentage"] = (country_grouped["value"] / country_grouped["value"].sum() * 100).round(1)
        country_data = country_grouped
    
    # Create charts
    import plotly.express as px
    import plotly.graph_objects as go
    
    # Risk distribution chart
    risk_chart = None
    if risk_data is not None and not risk_data.empty:
        colors = {"Low": "#38a169", "Medium": "#d69e2e", "High": "#c53030"}
        risk_chart = go.Figure(data=[go.Pie(
            labels=risk_data["risk_level"],
            values=risk_data["value"],
            hole=0.5,
            marker_colors=[colors.get(r, "#718096") for r in risk_data["risk_level"]],
            textinfo="label+percent",
            textposition="outside"
        )])
        risk_chart.update_layout(
            title=t("risk_distribution", lang),
            showlegend=False,
            margin=dict(t=50, b=20, l=20, r=20),
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
    
    # Volatility chart
    volatility_chart = None
    if volatility_data is not None and not volatility_data.empty:
        vol_colors = {"Low (<10%)": "#38a169", "Medium (10-25%)": "#d69e2e", "High (>25%)": "#c53030"}
        volatility_chart = go.Figure(data=[go.Bar(
            x=volatility_data["volatility_bucket"],
            y=volatility_data["value"],
            marker_color=[vol_colors.get(v, "#718096") for v in volatility_data["volatility_bucket"]],
            text=[f"{currency_symbol}{v:,.0f}" for v in volatility_data["value"]],
            textposition="auto"
        )])
        volatility_chart.update_layout(
            title=t("volatility_breakdown", lang),
            xaxis_title="",
            yaxis_title="",
            margin=dict(t=50, b=30, l=60, r=20),
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
    
    # Geographic map - using scatter_geo with bubble markers
    geo_map = None
    if country_data is not None and not country_data.empty:
        # Map ISO-2 country codes to coordinates for scatter plot
        country_coords = {
            "US": (37.0902, -95.7129, "United States"),
            "DE": (51.1657, 10.4515, "Germany"),
            "FR": (46.2276, 2.2137, "France"),
            "NL": (52.1326, 5.2913, "Netherlands"),
            "DK": (56.2639, 9.5018, "Denmark"),
            "HU": (47.1625, 19.5033, "Hungary"),
            "AT": (47.5162, 14.5501, "Austria"),
            "CZ": (49.8175, 15.4730, "Czech Republic"),
            "CH": (46.8182, 8.2275, "Switzerland"),
            "TW": (23.6978, 120.9605, "Taiwan"),
            "KR": (35.9078, 127.7669, "South Korea"),
            "JP": (36.2048, 138.2529, "Japan"),
            "GB": (55.3781, -3.4360, "United Kingdom"),
            "IT": (41.8719, 12.5674, "Italy"),
            "ES": (40.4637, -3.7492, "Spain"),
        }
        
        # Prepare data for scatter geo
        lats, lons, texts, sizes, colors, country_names = [], [], [], [], [], []
        max_val = country_data["value"].max()
        
        for _, row in country_data.iterrows():
            code = row["country"]
            if code in country_coords:
                lat, lon, name = country_coords[code]
                lats.append(lat)
                lons.append(lon)
                texts.append(f"{name}: {currency_symbol}{row['value']:,.0f} ({row['percentage']:.1f}%)")
                # Scale bubble size (min 15, max 50)
                size = 15 + (row["value"] / max_val) * 35
                sizes.append(size)
                colors.append(row["value"])
                country_names.append(name)
        
        geo_map = go.Figure(data=go.Scattergeo(
            lat=lats,
            lon=lons,
            text=texts,
            marker=dict(
                size=sizes,
                color=colors,
                colorscale="Blues",
                showscale=True,
                colorbar=dict(title=f"Value ({currency_symbol})"),
                line=dict(width=1, color="#1a365d"),
                opacity=0.8
            ),
            hovertemplate="%{text}<extra></extra>",
            name=""
        ))
        geo_map.update_layout(
            title=t("asset_map", lang),
            geo=dict(
                showframe=False,
                showcoastlines=True,
                coastlinecolor="#cccccc",
                showland=True,
                landcolor="#f0f0f0",
                showocean=True,
                oceancolor="#e6f3ff",
                showcountries=True,
                countrycolor="#dddddd",
                projection_type='natural earth',
                bgcolor="rgba(0,0,0,0)",
                center=dict(lat=40, lon=10),  # Center on Europe/Atlantic
                lonaxis_range=[-120, 150],
                lataxis_range=[10, 70]
            ),
            margin=dict(t=50, b=0, l=0, r=0),
            height=400,
            paper_bgcolor="rgba(0,0,0,0)"
        )
    
    # Build layout
    charts_row1 = []
    if risk_chart:
        charts_row1.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=risk_chart, config={"displayModeBar": False})
                    ])
                ], className="border-0 shadow-sm h-100", style={"borderRadius": "8px"})
            ], md=4, className="mb-4")
        )
    
    charts_row1.append(
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        figure=create_sector_bar_chart(sector_allocation),
                        config={"displayModeBar": False}
                    )
                ])
            ], className="border-0 shadow-sm h-100", style={"borderRadius": "8px"})
        ], md=4, className="mb-4")
    )
    
    if volatility_chart:
        charts_row1.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=volatility_chart, config={"displayModeBar": False})
                    ])
                ], className="border-0 shadow-sm h-100", style={"borderRadius": "8px"})
            ], md=4, className="mb-4")
        )
    
    # Row 2: Region and Map
    charts_row2 = [
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        figure=create_region_bar_chart(region_allocation),
                        config={"displayModeBar": False}
                    )
                ])
            ], className="border-0 shadow-sm h-100", style={"borderRadius": "8px"})
        ], md=4, className="mb-4")
    ]
    
    if geo_map:
        charts_row2.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=geo_map, config={"displayModeBar": False})
                    ])
                ], className="border-0 shadow-sm h-100", style={"borderRadius": "8px"})
            ], md=8, className="mb-4")
        )
    
    return html.Div([
        # Header
        dbc.Row([
            dbc.Col([
                html.H4(t("portfolio_diversity", lang), className="mb-1", style={"color": "#1a365d"}),
                html.P(
                    t("geographic_distribution", lang) if lang == "en" else "Portfólió sokszínűsége és kockázati megoszlása",
                    className="text-muted mb-4"
                )
            ])
        ]),
        
        # Charts Row 1: Risk, Sector, Volatility
        dbc.Row(charts_row1),
        
        # Charts Row 2: Region and Map
        dbc.Row(charts_row2)
    ])


def render_ownership_tab(currency_symbol, lang="en"):
    """Render the Ownership tab content with company ownership graph."""
    import plotly.graph_objects as go
    
    # Load ownership data
    ownership_data = load_ownership()
    
    if not ownership_data:
        return create_empty_state(t("no_data", lang))
    
    companies = ownership_data.get("companies", [])
    
    if not companies:
        return create_empty_state(t("no_data", lang))
    
    # Create ownership visualization using Sankey diagram
    # Build nodes and links for the ownership flow
    client_name = load_client().get("name", "Client")
    
    # Nodes: Client + all companies
    node_labels = [client_name]
    node_colors = ["#1a365d"]  # Client color
    
    # Categorize companies
    controlled = []  # >50% ownership
    significant = []  # 25-50%
    minority = []  # <25%
    
    for company in companies:
        node_labels.append(company["name"])
        ownership_pct = company.get("ownership_percentage", 0)
        
        if ownership_pct >= 50:
            node_colors.append("#38a169")  # Green for controlled
            controlled.append(company)
        elif ownership_pct >= 25:
            node_colors.append("#d69e2e")  # Yellow for significant
            significant.append(company)
        else:
            node_colors.append("#3182ce")  # Blue for minority
            minority.append(company)
    
    # Build links (from client to each company)
    sources = []
    targets = []
    values = []
    link_colors = []
    
    for i, company in enumerate(companies):
        sources.append(0)  # From client
        targets.append(i + 1)  # To company
        ownership_pct = company.get("ownership_percentage", 0)
        values.append(ownership_pct)
        
        if ownership_pct >= 50:
            link_colors.append("rgba(56, 161, 105, 0.5)")
        elif ownership_pct >= 25:
            link_colors.append("rgba(214, 158, 46, 0.5)")
        else:
            link_colors.append("rgba(49, 130, 206, 0.5)")
    
    # Create Sankey diagram
    sankey_fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=30,
            line=dict(color="white", width=0.5),
            label=node_labels,
            color=node_colors,
            hovertemplate="%{label}<extra></extra>"
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors,
            hovertemplate="%{source.label} → %{target.label}<br>Ownership: %{value:.1f}%<extra></extra>"
        )
    )])
    
    sankey_fig.update_layout(
        title=dict(
            text=t("company_ownership", lang),
            font=dict(size=18, color="#1a365d")
        ),
        font=dict(size=14),
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=50, r=50, t=60, b=30)
    )
    
    # Create bar chart of ownership percentages
    bar_fig = go.Figure()
    
    sorted_companies = sorted(companies, key=lambda x: x.get("ownership_percentage", 0), reverse=True)
    
    bar_fig.add_trace(go.Bar(
        y=[c["name"] for c in sorted_companies],
        x=[c.get("ownership_percentage", 0) for c in sorted_companies],
        orientation='h',
        marker=dict(
            color=[
                "#38a169" if c.get("ownership_percentage", 0) >= 50 
                else "#d69e2e" if c.get("ownership_percentage", 0) >= 25 
                else "#3182ce" 
                for c in sorted_companies
            ],
            line=dict(width=1, color="white")
        ),
        text=[f"{c.get('ownership_percentage', 0):.1f}%" for c in sorted_companies],
        textposition="auto",
        hovertemplate="%{y}<br>Ownership: %{x:.1f}%<extra></extra>"
    ))
    
    bar_fig.update_layout(
        title=dict(
            text=t("ownership_percentage", lang),
            font=dict(size=16, color="#1a365d")
        ),
        xaxis=dict(
            title="",
            ticksuffix="%",
            range=[0, 100]
        ),
        yaxis=dict(title="", autorange="reversed"),
        height=max(300, len(companies) * 40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=200, r=50, t=50, b=30)
    )
    
    # Calculate summary metrics
    total_companies = len(companies)
    controlled_count = len(controlled)
    minority_count = len(minority)
    avg_ownership = sum(c.get("ownership_percentage", 0) for c in companies) / total_companies if total_companies > 0 else 0
    
    return html.Div([
        # Header
        dbc.Row([
            dbc.Col([
                html.H4(t("company_ownership", lang), className="mb-1", style={"color": "#1a365d"}),
                html.P(
                    t("ownership_subtitle", lang),
                    className="text-muted mb-4"
                )
            ])
        ]),
        
        # Summary cards
        dbc.Row([
            # Average Ownership - First on mobile
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{avg_ownership:.1f}%", className="mb-0", style={"color": "#1a365d"}),
                        html.P("Average Ownership" if lang == "en" else "Átlagos Tulajdon", className="text-muted mb-1 small"),
                    ])
                ], className="border-0 shadow-sm text-center", style={"borderRadius": "8px"})
            ], xs=12, sm=4, md=4, className="mb-3", style={"order": "0"}),
            # Controlled Companies - Second row on mobile
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                       
                        html.H4(f"{controlled_count}", className="mb-0", style={"color": "#38a169"}),
                        html.Small(">50% ownership", className="text-muted")
                    ])
                ], className="border-0 shadow-sm text-center", style={"borderRadius": "8px"})
            ], xs=6, sm=4, md=4, className="mb-3", style={"order": "1"}),
            # Minority Stakes - Second row on mobile
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        
                        html.H4(f"{minority_count}", className="mb-0", style={"color": "#3182ce"}),
                        html.Small("<25% ownership", className="text-muted")
                    ])
                ], className="border-0 shadow-sm text-center", style={"borderRadius": "8px"})
            ], xs=6, sm=4, md=4, className="mb-3", style={"order": "2"}),
        ], className="mb-4"),
        
        # Ownership flow chart (Sankey)
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=sankey_fig, config={"displayModeBar": False})
                    ])
                ], className="border-0 shadow-sm", style={"borderRadius": "8px"})
            ], lg=7, md=12, className="mb-4"),
            
            # Ownership bar chart
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=bar_fig, config={"displayModeBar": False})
                    ])
                ], className="border-0 shadow-sm", style={"borderRadius": "8px"})
            ], lg=5, md=12, className="mb-4")
        ]),
        
        # Legend
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Span("● ", style={"color": "#38a169", "fontSize": "1.2rem"}),
                    html.Span("Controlled (>50%)" if lang == "en" else "Irányított (>50%)", className="me-4"),
                    html.Span("● ", style={"color": "#d69e2e", "fontSize": "1.2rem"}),
                    html.Span("Significant (25-50%)" if lang == "en" else "Jelentős (25-50%)", className="me-4"),
                    html.Span("● ", style={"color": "#3182ce", "fontSize": "1.2rem"}),
                    html.Span("Minority (<25%)" if lang == "en" else "Kisebbségi (<25%)")
                ], className="text-center text-muted")
            ])
        ])
    ])


def render_insights_tab(holdings, nav, lang="en", currency_symbol="€"):
    """Render the Insights tab content."""
    
    if holdings.empty:
        return create_empty_state(t("no_insights", lang))
    
    # Generate insights
    client = load_client()
    insights = generate_insights(holdings, nav, client, currency_symbol=currency_symbol)
    
    return html.Div([
        # Header
        dbc.Row([
            dbc.Col([
                html.H4(t("portfolio_insights", lang), className="mb-1", style={"color": "#1a365d"}),
                html.P(
                    t("insights_subtitle", lang),
                    className="text-muted mb-4"
                )
            ])
        ]),
        
        # Insights panel
        create_insights_panel(insights)
    ])


def render_reports_tab(holdings, currency_symbol, lang="en"):
    """Render the Reports tab content."""
    
    total_value = calculate_total_value(holdings)
    ytd_return = 0  # Placeholder
    allocation = calculate_asset_allocation(holdings)
    
    nav = load_nav()
    filtered_nav = filter_nav(nav, None, None)
    if not filtered_nav.empty:
        ytd_return = calculate_ytd_return(filtered_nav)
    
    return html.Div([
        # Export section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H6(t("export_data", lang), className="mb-0"),
                        className="bg-white border-bottom"
                    ),
                    dbc.CardBody([
                        html.P(
                            "Töltsd le a portfólió adatokat CSV formátumban elemzéshez." if lang == "hu" else 
                            "Download your portfolio data in CSV format for external analysis.",
                            className="text-muted mb-4"
                        ),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    [html.I(className="bi bi-download me-2"), t("export_assets_csv", lang)],
                                    id="btn-export-holdings",
                                    color="primary",
                                    className="me-3"
                                )
                            ])
                        ])
                    ])
                ], className="border-0 shadow-sm", style={"borderRadius": "8px"})
            ], lg=6, md=12, className="mb-4"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H6("PDF Jelentések" if lang == "hu" else "PDF Reports", className="mb-0"),
                        className="bg-white border-bottom"
                    ),
                    dbc.CardBody([
                        html.P(
                            "Készíts formázott PDF jelentéseket." if lang == "hu" else
                            "Generate formatted PDF reports for your records.",
                            className="text-muted mb-4"
                        ),
                        dbc.Button(
                            [html.I(className="bi bi-file-earmark-pdf me-2"), t("export_pdf", lang)],
                            color="secondary",
                            disabled=True
                        ),
                        html.Small(
                            " (" + t("coming_soon", lang) + ")",
                            className="text-muted ms-2"
                        )
                    ])
                ], className="border-0 shadow-sm", style={"borderRadius": "8px"})
            ], lg=6, md=12, className="mb-4")
        ]),
        
        # Quarterly snapshot
        dbc.Row([
            dbc.Col([
                create_quarterly_snapshot(
                    total_value,
                    ytd_return,
                    allocation,
                    len(holdings),
                    lang,
                    currency_symbol
                )
            ], lg=6, md=12)
        ])
    ])


def render_about_tab(lang="en"):
    """Render the About/Settings tab content."""
    
    client = load_client()
    target = client.get("target_allocation", {})
    
    return html.Div([
        dbc.Row([
            # Client profile
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H6("Ügyfél Profil" if lang == "hu" else "Client Profile", className="mb-0"),
                        className="bg-white border-bottom"
                    ),
                    dbc.CardBody([
                        html.Div([
                            html.P("Ügyfél ID" if lang == "hu" else "Client ID", className="text-muted small mb-1"),
                            html.P(client["id"], className="mb-3 fw-semibold")
                        ]),
                        html.Div([
                            html.P("Ügyfél Neve" if lang == "hu" else "Client Name", className="text-muted small mb-1"),
                            html.P(client["name"], className="mb-3 fw-semibold")
                        ]),
                        html.Div([
                            html.P(t("risk_profile", lang), className="text-muted small mb-1"),
                            dbc.Badge(
                                client["risk_profile"],
                                color="primary",
                                className="mb-3"
                            )
                        ]),
                        html.Div([
                            html.P("Alap Pénznem" if lang == "hu" else "Base Currency", className="text-muted small mb-1"),
                            html.P(client["base_currency"], className="mb-3 fw-semibold")
                        ]),
                        html.Div([
                            html.P("Kapcsolat Kezdete" if lang == "hu" else "Relationship Start", className="text-muted small mb-1"),
                            html.P(client["relationship_start_date"], className="mb-0 fw-semibold")
                        ])
                    ])
                ], className="border-0 shadow-sm h-100", style={"borderRadius": "8px"})
            ], lg=4, md=6, className="mb-4"),
            
            # Target allocation
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H6(t("target_allocation", lang), className="mb-0"),
                        className="bg-white border-bottom"
                    ),
                    dbc.CardBody([
                        html.P(
                            f"A {client['risk_profile']} kockázati profil alapján:" if lang == "hu" else
                            f"Based on {client['risk_profile']} risk profile:",
                            className="text-muted mb-4"
                        ),
                        *[
                            html.Div([
                                html.Div([
                                    html.Span(asset_type, className="me-2"),
                                    html.Span(f"{pct * 100:.0f}%", className="fw-semibold float-end")
                                ], className="mb-2"),
                                dbc.Progress(
                                    value=pct * 100,
                                    className="mb-3",
                                    style={"height": "8px"}
                                )
                            ])
                            for asset_type, pct in target.items()
                        ]
                    ])
                ], className="border-0 shadow-sm h-100", style={"borderRadius": "8px"})
            ], lg=4, md=6, className="mb-4"),
            
            # Disclaimer
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H6("Fontos Közlemény" if lang == "hu" else "Important Notice", className="mb-0"),
                        className="bg-white border-bottom"
                    ),
                    dbc.CardBody([
                        html.Div([
                            html.I(className="bi bi-exclamation-triangle-fill text-warning me-2"),
                            html.Strong(t("disclaimer", lang))
                        ], className="mb-3"),
                        html.P([
                            "Ez a műszerfal " if lang == "hu" else "This dashboard displays ",
                            html.Strong("demo adatokat" if lang == "hu" else "demo data"),
                            " jelenít meg, amelyek csak bemutatási célokat szolgálnak." if lang == "hu" else " generated for demonstration purposes only."
                        ], className="text-muted"),
                        html.P(
                            "Az itt megjelenített információk nem minősülnek befektetési tanácsnak, "
                            "és nem szolgálhatnak befektetési döntések alapjául." if lang == "hu" else
                            "The information presented here does not constitute investment advice "
                            "and should not be used as the basis for any investment decision.",
                            className="text-muted"
                        ),
                        html.P(
                            "A múltbeli teljesítmény nem garantálja a jövőbeli eredményeket. Minden befektetés "
                            "kockázattal jár, beleértve a tőkevesztés lehetőségét." if lang == "hu" else
                            "Past performance is not indicative of future results. All investments "
                            "carry risk, including the potential loss of principal.",
                            className="text-muted mb-0"
                        )
                    ])
                ], className="border-0 shadow-sm h-100", style={"borderRadius": "8px"})
            ], lg=4, md=12, className="mb-4")
        ])
    ])


# Export callbacks
@callback(
    Output("download-holdings", "data"),
    Input("btn-export-holdings", "n_clicks"),
    State("asset-type-filter", "value"),
    prevent_initial_call=True
)
def export_holdings(n_clicks, asset_type):
    """Export holdings to CSV."""
    if n_clicks:
        holdings = load_holdings()
        filtered = filter_holdings(holdings, None, asset_type, None)
        
        return dcc.send_data_frame(
            filtered.to_csv,
            "sqn_trust_holdings.csv",
            index=False
        )
    return None


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🏦 SQN Trust Portfolio Dashboard")
    print("=" * 50)
    print("\n📊 Starting server...")
    print("🌐 Open http://localhost:8051 in your browser")
    print("\nPress Ctrl+C to stop the server.\n")
    
    app.run(debug=True, host="0.0.0.0", port=8051)

 