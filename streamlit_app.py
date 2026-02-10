#!/usr/bin/env python3
"""
SQN Trust Portfolio Dashboard - Streamlit Version
A premium wealth management dashboard for portfolio visualization and analysis.
"""

from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Import services
from app.services.data_loader import (
    load_client, load_accounts, load_holdings, load_transactions, load_nav,
    load_ownership, load_real_estate_locations, get_asset_type_options, convert_currency
)
from app.services.filters import filter_holdings, filter_transactions, filter_nav, parse_date_range
from app.services.metrics import (
    calculate_total_value, calculate_unrealized_pnl, calculate_returns_from_nav,
    calculate_ytd_return, calculate_volatility, calculate_max_drawdown,
    calculate_asset_allocation, calculate_region_allocation, calculate_sector_allocation,
    get_top_holdings, calculate_concentration, calculate_liquidity_score,
    calculate_cash_percentage, generate_insights,
    calculate_cashflow_summary, calculate_income_summary
)
from app.services.translations import t

# Import components
from app.components.charts import (
    create_allocation_donut, create_nav_line_chart, create_region_bar_chart,
    create_sector_bar_chart, create_cashflow_chart, create_property_type_donut,
    create_geography_bar, create_account_breakdown_donut
)

# Page configuration
st.set_page_config(
    page_title="SQN Trust | Portfolio Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main container */
    .main {
        background-color: #f8fafc;
    }
    
    /* Header styling */
    .stApp header {
        background-color: #ffffff;
        border-bottom: 1px solid #e2e8f0;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        color: #1a365d;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        color: #718096;
        font-weight: 500;
        border-radius: 8px 8px 0 0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1a365d;
        color: white;
    }
    
    /* Cards */
    .element-container {
        border-radius: 8px;
    }
    
    /* Remove padding from top */
    .block-container {
        padding-top: 2rem;
    }
    
    /* Custom title styling */
    h1 {
        color: #1a365d;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    h2, h3 {
        color: #2d5a87;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'currency' not in st.session_state:
    st.session_state.currency = 'EUR'
if 'asset_type' not in st.session_state:
    st.session_state.asset_type = 'all'

# Load client data
client = load_client()

# Header
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown(f"# 🏦 SQN Trust")
    st.markdown(f"**{client['name']}** | {t('subtitle', st.session_state.language)}")

with col2:
    st.write("")  # Spacer

with col3:
    lang_col1, lang_col2 = st.columns(2)
    with lang_col1:
        if st.button("🇬🇧 EN", use_container_width=True, type="primary" if st.session_state.language == 'en' else "secondary"):
            st.session_state.language = 'en'
            st.rerun()
    with lang_col2:
        if st.button("🇭🇺 HU", use_container_width=True, type="primary" if st.session_state.language == 'hu' else "secondary"):
            st.session_state.language = 'hu'
            st.rerun()

st.divider()

# Sidebar filters
with st.sidebar:
    st.image("https://via.placeholder.com/200x80/1a365d/ffffff?text=SQN+Trust", use_container_width=True)
    
    st.markdown("### Filters")
    
    # Asset type filter
    asset_type_options = get_asset_type_options()
    asset_type_dict = {opt['label']: opt['value'] for opt in asset_type_options}
    selected_asset_label = st.selectbox(
        "Asset Type",
        options=list(asset_type_dict.keys()),
        index=0
    )
    st.session_state.asset_type = asset_type_dict[selected_asset_label]
    
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
    
    start_date, end_date = parse_date_range(period)
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=start_date)
    with col2:
        end_date = st.date_input("End Date", value=end_date)
    
    date_range = (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    
    st.divider()
    
    st.markdown("### About")
    st.info(f"""
    **Client:** {client['name']}  
    **Risk Profile:** {client['risk_profile']}  
    **Base Currency:** {client['base_currency']}
    """)

# Load and filter data
lang = st.session_state.language
currency = st.session_state.currency
asset_type = st.session_state.asset_type

holdings = load_holdings()
transactions = load_transactions()
nav = load_nav()
accounts = load_accounts()

# Apply filters
filtered_holdings = filter_holdings(holdings, None, asset_type, date_range)
filtered_transactions = filter_transactions(transactions, None, None, date_range)
filtered_nav = filter_nav(nav, None, date_range)

# Currency conversion
conversion_rates = {
    "EUR": 1.0,
    "USD": 1.09,
    "HUF": 395.0
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

# Main tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    t("tab_summary", lang),
    t("tab_assets", lang),
    t("tab_ownership", lang),
    t("tab_map", lang),
    t("tab_diversity", lang),
    t("tab_insights", lang),
    t("tab_reports", lang),
    t("tab_about", lang)
])

# Tab 1: Summary
with tab1:
    if filtered_holdings.empty:
        st.warning(t("no_assets", lang))
    else:
        # Calculate metrics
        total_value = calculate_total_value(filtered_holdings)
        pnl_abs, pnl_pct = calculate_unrealized_pnl(filtered_holdings)
        returns_1y = calculate_returns_from_nav(filtered_nav, 365)
        ytd_return = calculate_ytd_return(filtered_nav)
        volatility = calculate_volatility(filtered_nav)
        cash_pct = calculate_cash_percentage(filtered_holdings)
        
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label=t("total_portfolio_value", lang),
                value=f"{currency_symbol}{total_value:,.0f}",
                help=t("tooltip_portfolio_value", lang)
            )
        
        with col2:
            st.metric(
                label=t("1y_return", lang),
                value=f"{returns_1y['return_pct']:+.1f}%",
                delta=f"{returns_1y['return_pct']:.1f}%",
                help=t("tooltip_1y_return", lang)
            )
        
        with col3:
            st.metric(
                label=t("ytd_return", lang),
                value=f"{ytd_return:+.1f}%",
                delta=f"{ytd_return:.1f}%",
                help=t("tooltip_ytd_return", lang)
            )
        
        with col4:
            st.metric(
                label=t("volatility", lang),
                value=f"{volatility:.1f}%",
                help=t("tooltip_volatility", lang)
            )
        
        st.divider()
        
        # Charts
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.markdown(f"#### {t('asset_allocation', lang)}")
            allocation = calculate_asset_allocation(filtered_holdings)
            fig = create_allocation_donut(allocation)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown(f"#### {t('portfolio_value_over_time', lang)}")
            fig = create_nav_line_chart(filtered_nav)
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Top holdings table
        st.markdown(f"#### {t('top_holdings', lang) if 'top_holdings' in dir() else 'Top Holdings'}")
        top_holdings_df = get_top_holdings(filtered_holdings, 10)
        st.dataframe(top_holdings_df, use_container_width=True, hide_index=True)

# Tab 2: Assets
with tab2:
    if filtered_holdings.empty:
        st.warning(t("no_assets", lang))
    else:
        # Breakdown charts based on asset type
        col1, col2 = st.columns(2)
        
        if asset_type == "Shares" or (asset_type == "all" and 
            filtered_holdings[filtered_holdings["asset_type"] == "Shares"]["valuation_current"].sum() > 
            filtered_holdings["valuation_current"].sum() * 0.5):
            with col1:
                st.markdown("#### Sector Allocation")
                sector_allocation = calculate_sector_allocation(filtered_holdings)
                fig = create_sector_bar_chart(sector_allocation)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### Region Allocation")
                region_allocation = calculate_region_allocation(filtered_holdings)
                fig = create_region_bar_chart(region_allocation)
                st.plotly_chart(fig, use_container_width=True)
        
        elif asset_type == "RealEstate":
            with col1:
                st.markdown("#### Property Type")
                fig = create_property_type_donut(filtered_holdings)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### Geography")
                fig = create_geography_bar(filtered_holdings)
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            with col1:
                st.markdown("#### Sector Allocation")
                sector_allocation = calculate_sector_allocation(filtered_holdings)
                fig = create_sector_bar_chart(sector_allocation)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### Region Allocation")
                region_allocation = calculate_region_allocation(filtered_holdings)
                fig = create_region_bar_chart(region_allocation)
                st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Full holdings table
        st.markdown(f"#### {t('all_assets', lang)}")
        st.dataframe(
            filtered_holdings[[
                'asset_name', 'asset_type', 'quantity', 
                'valuation_current', 'last_valuation_date'
            ]],
            use_container_width=True,
            hide_index=True
        )

# Tab 3: Ownership
with tab3:
    ownership_data = load_ownership()
    
    if not ownership_data or not ownership_data.get("companies"):
        st.warning(t("no_data", lang))
    else:
        companies = ownership_data.get("companies", [])
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        total_companies = len(companies)
        controlled_count = len([c for c in companies if c.get("ownership_percentage", 0) >= 50])
        minority_count = len([c for c in companies if c.get("ownership_percentage", 0) < 25])
        avg_ownership = sum(c.get("ownership_percentage", 0) for c in companies) / total_companies if total_companies > 0 else 0
        
        with col1:
            st.metric("Average Ownership" if lang == "en" else "Átlagos Tulajdon", f"{avg_ownership:.1f}%")
        
        with col2:
            st.metric("Controlled Companies" if lang == "en" else "Irányított Cégek", controlled_count, help=">50% ownership")
        
        with col3:
            st.metric("Minority Stakes" if lang == "en" else "Kisebbségi Részesedések", minority_count, help="<25% ownership")
        
        st.divider()
        
        # Sankey diagram
        st.markdown(f"#### {t('company_ownership', lang)}")
        
        client_name = client.get("name", "Client")
        
        # Build Sankey data
        node_labels = [client_name]
        node_colors = ["#1a365d"]
        
        sources = []
        targets = []
        values = []
        link_colors = []
        
        for i, company in enumerate(companies):
            node_labels.append(company["name"])
            ownership_pct = company.get("ownership_percentage", 0)
            
            if ownership_pct >= 50:
                node_colors.append("#38a169")
                link_colors.append("rgba(56, 161, 105, 0.5)")
            elif ownership_pct >= 25:
                node_colors.append("#d69e2e")
                link_colors.append("rgba(214, 158, 46, 0.5)")
            else:
                node_colors.append("#3182ce")
                link_colors.append("rgba(49, 130, 206, 0.5)")
            
            sources.append(0)
            targets.append(i + 1)
            values.append(ownership_pct)
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=20,
                thickness=30,
                line=dict(color="white", width=0.5),
                label=node_labels,
                color=node_colors
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=link_colors
            )
        )])
        
        fig.update_layout(
            height=500,
            font=dict(size=14)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Company list
        st.markdown("#### Company Details")
        company_df = pd.DataFrame(companies)
        if not company_df.empty:
            st.dataframe(company_df, use_container_width=True, hide_index=True)

# Tab 4: Map
with tab4:
    real_estate = filtered_holdings[filtered_holdings["asset_type"] == "RealEstate"].copy()
    
    if real_estate.empty:
        st.warning("No real estate data available" if lang == "en" else "Nincs ingatlan adat")
    else:
        locations = load_real_estate_locations()
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        total_properties = len(real_estate)
        total_value = real_estate["valuation_current"].sum()
        avg_value = real_estate["valuation_current"].mean()
        
        with col1:
            st.metric(t("total_real_estate_value", lang), f"{currency_symbol}{total_value:,.0f}")
        
        with col2:
            st.metric(t("total_properties", lang), total_properties)
        
        with col3:
            st.metric("Avg. Value" if lang == "en" else "Átl. Érték", f"{currency_symbol}{avg_value:,.0f}")
        
        st.divider()
        
        # Prepare location data
        if locations:
            location_df = pd.DataFrame(locations)
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
        
        merged["lat"] = merged["lat"].fillna(47.4979)
        merged["lon"] = merged["lon"].fillna(19.0402)
        
        # Create map
        st.markdown(f"#### {t('real_estate_map', lang)}")
        st.map(merged[["lat", "lon"]], zoom=4)
        
        # Property cards
        st.markdown("#### Properties" if lang == "en" else "#### Ingatlanok")
        
        for idx, row in merged.head(6).iterrows():
            with st.expander(f"**{row['asset_name']}** - {currency_symbol}{row['valuation_current']:,.0f}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Type:** {row.get('property_type', 'N/A')}")
                    st.write(f"**Location:** {row.get('city', row.get('address', 'N/A'))}")
                with col2:
                    if 'size_sqm' in row and pd.notna(row.get('size_sqm')):
                        st.write(f"**Size:** {row['size_sqm']:,.0f} m²")

# Tab 5: Diversity
with tab5:
    if filtered_holdings.empty:
        st.warning(t("no_assets", lang))
    else:
        st.markdown(f"#### {t('portfolio_diversity', lang)}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Sector Distribution")
            sector_allocation = calculate_sector_allocation(filtered_holdings)
            fig = create_sector_bar_chart(sector_allocation)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("##### Region Distribution")
            region_allocation = calculate_region_allocation(filtered_holdings)
            fig = create_region_bar_chart(region_allocation)
            st.plotly_chart(fig, use_container_width=True)
        
        # Geographic map
        if "country" in filtered_holdings.columns:
            st.divider()
            st.markdown("##### Geographic Distribution")
            
            country_grouped = filtered_holdings[filtered_holdings["country"].notna()].groupby("country")["valuation_current"].sum().reset_index()
            country_grouped.columns = ["country", "value"]
            country_grouped = country_grouped.sort_values("value", ascending=False)
            
            st.bar_chart(country_grouped.set_index("country"))

# Tab 6: Insights
with tab6:
    if filtered_holdings.empty:
        st.warning(t("no_insights", lang) if "no_insights" in dir() else "No insights available")
    else:
        insights = generate_insights(filtered_holdings, filtered_nav, client, currency_symbol=currency_symbol)
        
        st.markdown(f"#### {t('portfolio_insights', lang)}")
        st.caption(t('insights_subtitle', lang))
        
        # Display insights in cards
        for i in range(0, len(insights), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i + j < len(insights):
                    insight = insights[i + j]
                    with col:
                        with st.container():
                            st.markdown(f"**{insight['title']}**")
                            st.caption(insight['text'])
                            st.divider()

# Tab 7: Reports
with tab7:
    st.markdown(f"#### {t('export_data', lang)}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### CSV Export")
        st.write(t("export_data", lang) if lang == "hu" else "Download your portfolio data in CSV format for external analysis.")
        
        csv = filtered_holdings.to_csv(index=False)
        st.download_button(
            label="📥 " + t("export_assets_csv", lang),
            data=csv,
            file_name="sqn_trust_holdings.csv",
            mime="text/csv"
        )
    
    with col2:
        st.markdown("##### PDF Reports")
        st.write("Generate formatted PDF reports for your records." if lang == "en" else "Készíts formázott PDF jelentéseket.")
        st.button("📄 " + t("export_pdf", lang), disabled=True, help=t("coming_soon", lang))

# Tab 8: About
with tab8:
    st.markdown(f"#### Client Profile" if lang == "en" else "#### Ügyfél Profil")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("##### Profile Details")
        st.write(f"**Client ID:** {client['id']}")
        st.write(f"**Name:** {client['name']}")
        st.write(f"**Risk Profile:** {client['risk_profile']}")
        st.write(f"**Base Currency:** {client['base_currency']}")
        st.write(f"**Relationship Start:** {client['relationship_start_date']}")
    
    with col2:
        st.markdown(f"##### {t('target_allocation', lang)}")
        target = client.get("target_allocation", {})
        for asset_type, pct in target.items():
            st.progress(pct, text=f"{asset_type}: {pct * 100:.0f}%")
    
    with col3:
        st.markdown("##### Important Notice" if lang == "en" else "##### Fontos Közlemény")
        st.warning(f"""
        ⚠️ **{t('disclaimer', lang)}**
        
        This dashboard displays demo data generated for demonstration purposes only.
        
        The information presented here does not constitute investment advice and should not be used as the basis for any investment decision.
        
        Past performance is not indicative of future results. All investments carry risk, including the potential loss of principal.
        """ if lang == "en" else """
        ⚠️ **{t('disclaimer', lang)}**
        
        Ez a műszerfal demo adatokat jelenít meg, amelyek csak bemutatási célokat szolgálnak.
        
        Az itt megjelenített információk nem minősülnek befektetési tanácsnak, és nem szolgálhatnak befektetési döntések alapjául.
        
        A múltbeli teljesítmény nem garantálja a jövőbeli eredményeket. Minden befektetés kockázattal jár, beleértve a tőkevesztés lehetőségét.
        """)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #718096; font-size: 0.875rem; padding: 2rem 0;">
    <p>SQN Trust Portfolio Dashboard | Demo Version</p>
    <p>© 2026 SQN Trust. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
