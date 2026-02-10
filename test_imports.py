#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
Run this before deploying to catch import errors early
"""

import sys

print("🧪 Testing imports for Streamlit app...")
print("=" * 50)

errors = []

# Test standard library
try:
    from datetime import datetime, timedelta
    print("✅ datetime")
except Exception as e:
    print(f"❌ datetime: {e}")
    errors.append(("datetime", e))

# Test third-party libraries
try:
    import streamlit as st
    print("✅ streamlit")
except Exception as e:
    print(f"❌ streamlit: {e}")
    errors.append(("streamlit", e))

try:
    import pandas as pd
    print("✅ pandas")
except Exception as e:
    print(f"❌ pandas: {e}")
    errors.append(("pandas", e))

try:
    import plotly.graph_objects as go
    print("✅ plotly")
except Exception as e:
    print(f"❌ plotly: {e}")
    errors.append(("plotly", e))

try:
    import numpy as np
    print("✅ numpy")
except Exception as e:
    print(f"❌ numpy: {e}")
    errors.append(("numpy", e))

# Test app services
try:
    from app.services.data_loader import (
        load_client, load_accounts, load_holdings, load_transactions, load_nav,
        load_ownership, load_real_estate_locations, get_asset_type_options
    )
    print("✅ app.services.data_loader")
except Exception as e:
    print(f"❌ app.services.data_loader: {e}")
    errors.append(("data_loader", e))

try:
    from app.services.filters import filter_holdings, filter_transactions, filter_nav, parse_date_range
    print("✅ app.services.filters")
except Exception as e:
    print(f"❌ app.services.filters: {e}")
    errors.append(("filters", e))

try:
    from app.services.metrics import (
        calculate_total_value, calculate_unrealized_pnl, calculate_returns_from_nav,
        calculate_ytd_return, calculate_volatility
    )
    print("✅ app.services.metrics")
except Exception as e:
    print(f"❌ app.services.metrics: {e}")
    errors.append(("metrics", e))

try:
    from app.services.translations import t
    print("✅ app.services.translations")
except Exception as e:
    print(f"❌ app.services.translations: {e}")
    errors.append(("translations", e))

# Test app components
try:
    from app.components.charts import (
        create_allocation_donut, create_nav_line_chart, create_region_bar_chart
    )
    print("✅ app.components.charts")
except Exception as e:
    print(f"❌ app.components.charts: {e}")
    errors.append(("charts", e))

# Test data loading
try:
    from app.services.data_loader import load_client
    client = load_client()
    print(f"✅ Data loading works - Client: {client.get('name', 'Unknown')}")
except Exception as e:
    print(f"❌ Data loading: {e}")
    errors.append(("data_loading", e))

print("=" * 50)

if errors:
    print(f"\n❌ {len(errors)} ERROR(S) FOUND:")
    for module, error in errors:
        print(f"  - {module}: {str(error)[:100]}")
    print("\n⚠️  Fix these errors before deploying!")
    sys.exit(1)
else:
    print("\n✅ ALL TESTS PASSED!")
    print("🚀 Ready to deploy to Streamlit Cloud!")
    sys.exit(0)
