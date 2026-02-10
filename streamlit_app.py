#!/usr/bin/env python3
"""
SQN Trust Portfolio Dashboard - Streamlit Version
A premium wealth management dashboard for portfolio visualization and analysis.
"""

from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import traceback

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="SQN Trust | Portfolio Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Error handling wrapper
def safe_execute(func, fallback=None, error_msg="An error occurred"):
    """Safely execute a function with error handling"""
    try:
        return func()
    except Exception as e:
        st.error(f"{error_msg}: {str(e)}")
        if fallback is not None:
            return fallback
        return None

# Import services with error handling
try:
    from app.services.data_loader import (
        load_client, load_accounts, load_holdings, load_transactions, load_nav,
        load_ownership, load_real_estate_locations, get_asset_type_options
    )
    from app.services.filters import filter_holdings, filter_transactions, filter_nav, parse_date_range
    from app.services.metrics import (
        calculate_total_value, calculate_unrealized_pnl, calculate_returns_from_nav,
        calculate_ytd_return, calculate_volatility,
        calculate_asset_allocation, calculate_region_allocation, calculate_sector_allocation,
        get_top_holdings, calculate_cash_percentage, generate_insights
    )
    from app.services.translations import t
    from app.components.charts import (
        create_allocation_donut, create_nav_line_chart, create_region_bar_chart,
        create_sector_bar_chart, create_property_type_donut,
        create_geography_bar, create_account_breakdown_donut
    )
    IMPORTS_OK = True
except Exception as e:
    st.error(f"Import Error: {str(e)}")
    IMPORTS_OK = False

if not IMPORTS_OK:
    st.stop()

# Custom CSS
st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    [data-testid="stMetricValue"] { font-size: 1.5rem; color: #1a365d; }
    h1 { color: #1a365d; font-weight: 700; }
    h2, h3 { color: #2d5a87; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'currency' not in st.session_state:
    st.session_state.currency = 'EUR'
if 'asset_type' not in st.session_state:
    st.session_state.asset_type = 'all'

# Load client data with error handling
try:
    client = load_client()
except Exception as e:
    st.error(f"Failed to load client data: {str(e)}")
    client = {"name": "Client", "risk_profile": "Moderate", "base_currency": "EUR"}

# Header
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown(f"# 🏦 SQN Trust")
    st.markdown(f"**{client.get('name', 'Client')}** | Portfolio Dashboard")

with col3:
    lang_col1, lang_col2 = st.columns(2)
    with lang_col1:
        if st.button("🇬🇧 EN", key="lang_en", type="primary" if st.session_state.language == 'en' else "secondary"):
            st.session_state.language = 'en'
            st.rerun()
    with lang_col2:
        if st.button("🇭🇺 HU", key="lang_hu", type="primary" if st.session_state.language == 'hu' else "secondary"):
            st.session_state.language = 'hu'
            st.rerun()

st.divider()

# Sidebar filters
with st.sidebar:
    st.markdown("## 🏦 SQN Trust")
    st.caption("Portfolio Dashboard")
    
    st.markdown("### Filters")
    
    # Asset type filter
    try:
        asset_type_options = get_asset_type_options()
        asset_type_dict = {opt['label']: opt['value'] for opt in asset_type_options}
        selected_asset_label = st.selectbox(
            "Asset Type",
            options=list(asset_type_dict.keys()),
            index=0
        )
        st.session_state.asset_type = asset_type_dict[selected_asset_label]
    except Exception as e:
        st.error(f"Filter error: {str(e)}")
        st.session_state.asset_type = 'all'
    
    # Currency selector
    st.session_state.currency = st.radio(
        "Currency",
        options=["EUR", "USD", "HUF"],
        horizontal=True
    )
    
    # Date range
    st.markdown("### Date Range")
    
    period = st.selectbox(
        "Quick Period",
        options=["1M", "3M", "6M", "1Y", "ALL"],
        index=3
    )
    
    try:
        start_date, end_date = parse_date_range(period)
    except:
        start_date = datetime.now() - timedelta(days=365)
        end_date = datetime.now()
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=start_date)
    with col2:
        end_date = st.date_input("End Date", value=end_date)
    
    date_range = (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    
    st.divider()
    
    st.markdown("### About")
    st.info(f"""
    **Client:** {client.get('name', 'N/A')}  
    **Risk Profile:** {client.get('risk_profile', 'N/A')}  
    **Base Currency:** {client.get('base_currency', 'EUR')}
    """)

# Load and filter data with error handling
lang = st.session_state.language
currency = st.session_state.currency
asset_type = st.session_state.asset_type

try:
    holdings = load_holdings()
    transactions = load_transactions()
    nav = load_nav()
    accounts = load_accounts()
except Exception as e:
    st.error(f"Data loading error: {str(e)}")
    st.stop()

# Apply filters
try:
    filtered_holdings = filter_holdings(holdings, None, asset_type, date_range)
    filtered_transactions = filter_transactions(transactions, None, None, date_range)
    filtered_nav = filter_nav(nav, None, date_range)
except Exception as e:
    st.warning(f"Filter error: {str(e)}")
    filtered_holdings = holdings
    filtered_transactions = transactions
    filtered_nav = nav

# Currency conversion
conversion_rates = {"EUR": 1.0, "USD": 1.09, "HUF": 395.0}
currency_symbols = {"EUR": "€", "USD": "$", "HUF": "Ft"}

if currency != "EUR":
    conversion_rate = conversion_rates.get(currency, 1.0)
    filtered_holdings = filtered_holdings.copy()
    filtered_holdings["valuation_current"] = filtered_holdings["valuation_current"] * conversion_rate
    filtered_holdings["valuation_cost_basis"] = filtered_holdings["valuation_cost_basis"] * conversion_rate
    filtered_nav = filtered_nav.copy()
    filtered_nav["value"] = filtered_nav["value"] * conversion_rate

currency_symbol = currency_symbols.get(currency, "€")

# Main tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📊 Summary",
    "💼 Assets",
    "🏢 Ownership",
    "🗺️ Map",
    "🌍 Diversity",
    "💡 Insights",
    "📈 Reports",
    "ℹ️ About"
])

# Tab 1: Summary
with tab1:
    if filtered_holdings.empty:
        st.warning("No assets found with current filters")
    else:
        try:
            # Calculate metrics
            total_value = calculate_total_value(filtered_holdings)
            pnl_abs, pnl_pct = calculate_unrealized_pnl(filtered_holdings)
            returns_1y = calculate_returns_from_nav(filtered_nav, 365)
            ytd_return = calculate_ytd_return(filtered_nav)
            volatility = calculate_volatility(filtered_nav)
            
            # KPI Cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Total Portfolio Value",
                    value=f"{currency_symbol}{total_value:,.0f}"
                )
            
            with col2:
                st.metric(
                    label="1Y Return",
                    value=f"{returns_1y['return_pct']:+.1f}%",
                    delta=f"{returns_1y['return_pct']:.1f}%"
                )
            
            with col3:
                st.metric(
                    label="YTD Return",
                    value=f"{ytd_return:+.1f}%",
                    delta=f"{ytd_return:.1f}%"
                )
            
            with col4:
                st.metric(
                    label="Volatility",
                    value=f"{volatility:.1f}%"
                )
            
            st.divider()
            
            # Charts
            col1, col2 = st.columns([2, 3])
            
            with col1:
                st.markdown("#### Asset Allocation")
                try:
                    allocation = calculate_asset_allocation(filtered_holdings)
                    fig = create_allocation_donut(allocation)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Chart error: {str(e)}")
            
            with col2:
                st.markdown("#### Portfolio Value Over Time")
                try:
                    fig = create_nav_line_chart(filtered_nav)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Chart error: {str(e)}")
            
            st.divider()
            
            # Top holdings
            st.markdown("#### Top Holdings")
            try:
                top_holdings_df = get_top_holdings(filtered_holdings, 10)
                st.dataframe(top_holdings_df, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Table error: {str(e)}")
                
        except Exception as e:
            st.error(f"Summary tab error: {str(e)}")

# Tab 2: Assets
with tab2:
    if filtered_holdings.empty:
        st.warning("No assets found")
    else:
        try:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Sector Allocation")
                try:
                    sector_allocation = calculate_sector_allocation(filtered_holdings)
                    fig = create_sector_bar_chart(sector_allocation)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Sector chart unavailable: {str(e)}")
            
            with col2:
                st.markdown("#### Region Allocation")
                try:
                    region_allocation = calculate_region_allocation(filtered_holdings)
                    fig = create_region_bar_chart(region_allocation)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Region chart unavailable: {str(e)}")
            
            st.divider()
            
            # Holdings table
            st.markdown("#### All Assets")
            display_cols = ['asset_name', 'asset_type', 'valuation_current', 'last_valuation_date']
            available_cols = [col for col in display_cols if col in filtered_holdings.columns]
            st.dataframe(filtered_holdings[available_cols], use_container_width=True, hide_index=True)
            
        except Exception as e:
            st.error(f"Assets tab error: {str(e)}")

# Tab 3: Ownership
with tab3:
    try:
        ownership_data = load_ownership()
        companies = ownership_data.get("companies", [])
        
        if not companies:
            st.warning("No ownership data available")
        else:
            col1, col2, col3 = st.columns(3)
            
            total_companies = len(companies)
            controlled_count = len([c for c in companies if c.get("ownership_percentage", 0) >= 50])
            avg_ownership = sum(c.get("ownership_percentage", 0) for c in companies) / total_companies if total_companies > 0 else 0
            
            with col1:
                st.metric("Average Ownership", f"{avg_ownership:.1f}%")
            with col2:
                st.metric("Controlled Companies", controlled_count)
            with col3:
                st.metric("Total Companies", total_companies)
            
            st.divider()
            
            # Sankey diagram
            st.markdown("#### Company Ownership Structure")
            try:
                client_name = client.get("name", "Client")
                node_labels = [client_name] + [c["name"] for c in companies]
                node_colors = ["#1a365d"] + ["#38a169" if c.get("ownership_percentage", 0) >= 50 else "#3182ce" for c in companies]
                
                sources = [0] * len(companies)
                targets = list(range(1, len(companies) + 1))
                values = [c.get("ownership_percentage", 0) for c in companies]
                
                fig = go.Figure(data=[go.Sankey(
                    node=dict(pad=20, thickness=30, label=node_labels, color=node_colors),
                    link=dict(source=sources, target=targets, value=values)
                )])
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Ownership chart unavailable: {str(e)}")
                
    except Exception as e:
        st.error(f"Ownership tab error: {str(e)}")

# Tab 4: Map
with tab4:
    try:
        real_estate = filtered_holdings[filtered_holdings["asset_type"] == "RealEstate"].copy()
        
        if real_estate.empty:
            st.warning("No real estate data available")
        else:
            col1, col2, col3 = st.columns(3)
            
            total_properties = len(real_estate)
            total_value = real_estate["valuation_current"].sum()
            avg_value = real_estate["valuation_current"].mean()
            
            with col1:
                st.metric("Total Real Estate Value", f"{currency_symbol}{total_value:,.0f}")
            with col2:
                st.metric("Total Properties", total_properties)
            with col3:
                st.metric("Avg. Value", f"{currency_symbol}{avg_value:,.0f}")
            
            st.divider()
            
            # Simple property list (avoid complex maps)
            st.markdown("#### Properties")
            for idx, row in real_estate.head(10).iterrows():
                with st.expander(f"**{row['asset_name']}** - {currency_symbol}{row['valuation_current']:,.0f}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Type:** {row.get('property_type', 'N/A')}")
                        st.write(f"**Location:** {row.get('city', 'N/A')}")
                    with col2:
                        st.write(f"**Value:** {currency_symbol}{row['valuation_current']:,.0f}")
                        
    except Exception as e:
        st.error(f"Map tab error: {str(e)}")

# Tab 5: Diversity
with tab5:
    if filtered_holdings.empty:
        st.warning("No data available")
    else:
        try:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### Sector Distribution")
                try:
                    sector_allocation = calculate_sector_allocation(filtered_holdings)
                    fig = create_sector_bar_chart(sector_allocation)
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    st.info("Sector data not available")
            
            with col2:
                st.markdown("##### Region Distribution")
                try:
                    region_allocation = calculate_region_allocation(filtered_holdings)
                    fig = create_region_bar_chart(region_allocation)
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    st.info("Region data not available")
                    
        except Exception as e:
            st.error(f"Diversity tab error: {str(e)}")

# Tab 6: Insights
with tab6:
    try:
        if filtered_holdings.empty:
            st.warning("No data for insights")
        else:
            st.markdown("#### Portfolio Insights")
            insights = generate_insights(filtered_holdings, filtered_nav, client, currency_symbol=currency_symbol)
            
            for i in range(0, len(insights), 3):
                cols = st.columns(3)
                for j, col in enumerate(cols):
                    if i + j < len(insights):
                        insight = insights[i + j]
                        with col:
                            st.markdown(f"**{insight['title']}**")
                            st.caption(insight['text'])
                            
    except Exception as e:
        st.error(f"Insights error: {str(e)}")

# Tab 7: Reports
with tab7:
    st.markdown("#### Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### CSV Export")
        st.write("Download portfolio data")
        
        try:
            csv = filtered_holdings.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="portfolio_holdings.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Export error: {str(e)}")
    
    with col2:
        st.markdown("##### PDF Reports")
        st.write("Coming soon...")
        st.button("📄 Generate PDF", disabled=True)

# Tab 8: About
with tab8:
    st.markdown("#### Client Profile")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Details")
        st.write(f"**Client:** {client.get('name', 'N/A')}")
        st.write(f"**Risk Profile:** {client.get('risk_profile', 'N/A')}")
        st.write(f"**Base Currency:** {client.get('base_currency', 'EUR')}")
    
    with col2:
        st.markdown("##### Disclaimer")
        st.warning("""
        ⚠️ **Demo Data**
        
        This dashboard displays demo data for demonstration purposes only.
        Not financial advice.
        """)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #718096; font-size: 0.875rem;">
    <p>SQN Trust Portfolio Dashboard | Demo Version</p>
</div>
""", unsafe_allow_html=True)
