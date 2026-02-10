# SQN Trust Portfolio Dashboard

A premium wealth management dashboard for portfolio visualization and analysis.

## 🚀 Two Versions Available

This repository contains **two versions** of the same dashboard:

1. **Dash Version** (`app/app.py`) - Full-featured with callbacks
2. **Streamlit Version** (`streamlit_app.py`) - Cloud-ready, simplified deployment ⭐

## Features

- 📊 **Portfolio Summary** - Real-time portfolio value, returns, and performance metrics
- 💼 **Asset Management** - Detailed asset breakdown with sector and region analysis
- 🏢 **Ownership Structure** - Company ownership visualization with Sankey diagrams  
-🗺️ **Real Estate Mapping** - Interactive maps showing property locations
- 🌍 **Diversity Analysis** - Portfolio diversity across sectors, regions, and risk levels
- 💡 **AI Insights** - Auto-generated portfolio insights and recommendations
- 📈 **Reports & Export** - CSV export and PDF report generation
- 🌐 **Multi-language** - English and Hungarian support
- 💱 **Multi-currency** - EUR, USD, and HUF support

## 🎯 Quick Start

### Option 1: Run Streamlit Version (Recommended for Cloud)

```bash
# Install dependencies
pip install -r requirements_streamlit.txt

# Run the app
streamlit run streamlit_app.py
```

Access at: **http://localhost:8501**

### Option 2: Run Dash Version

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app/app.py
```

Access at: **http://localhost:8051**

## ☁️ Deploy to Streamlit Cloud (Free!)

The easiest way to host this dashboard online:

### Step-by-Step Deployment

1. **Fork this repository** to your GitHub account

2. **Go to [Streamlit Cloud](https://streamlit.io/cloud)** and sign in with GitHub

3. **Click "New app"**

4. **Configure:**
   - Repository: `your-username/trust_found_demo`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
   - Python version: 3.10

5. **Advanced settings:**
   - Requirements file: `requirements_streamlit.txt`

6. **Click "Deploy"** 🎉

Your dashboard will be live at: `https://your-app-name.streamlit.app`

### No Environment Variables Needed!

All demo data is included in the repository - just deploy and go!

## 📁 Project Structure

```
trust_found_demo/
├── streamlit_app.py           # Streamlit version (cloud-ready)
├── app/
│   ├── app.py                 # Dash version
│   ├── components/            # Reusable UI components
│   │   ├── charts.py         # Plotly charts
│   │   ├── tables.py         # Data tables
│   │   ├── kpi_cards.py      # KPI components
│   │   └── layout.py         # Layout utilities
│   ├── services/             # Business logic
│   │   ├── data_loader.py    # Data loading
│   │   ├── filters.py        # Filtering logic
│   │   ├── metrics.py        # Calculations
│   │   └── translations.py   # i18n
│   └── data/                 # Demo CSV/JSON data
├── .streamlit/
│   └── config.toml           # Streamlit configuration
├── requirements.txt          # Dash dependencies
└── requirements_streamlit.txt # Streamlit dependencies
```

## 📊 Demo Data

The dashboard includes realistic demo data:

- **Holdings**: Stocks, real estate, liquid assets
- **NAV History**: Historical portfolio values
- **Transactions**: Buy/sell history
- **Ownership**: Company ownership structures
- **Real Estate**: Property locations and details

### Replace with Your Data

All data files are in `app/data/`:
- `holdings.csv` - Asset positions
- `nav.csv` - Net asset value history
- `transactions.csv` - Transaction history
- `accounts.csv` - Account information
- `client.json` - Client profile
- `ownership.json` - Company ownership
- `real_estate_locations.json` - Property locations

Simply replace these files with your own data following the same schema!

## 🎨 Customization

### Colors & Theme

**Streamlit**: Edit `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#1a365d"
backgroundColor = "#f8fafc"
```

**Dash**: Edit CSS in `app/components/layout.py`

### Language

Toggle between English 🇬🇧 and Hungarian 🇭🇺 in the app header.

Edit translations in `app/services/translations.py`

## 🔧 Development

### Install Development Dependencies

```bash
# For Streamlit version
pip install -r requirements_streamlit.txt

# For Dash version  
pip install -r requirements.txt
```

### Run in Development Mode

```bash
# Streamlit (auto-reloads on file changes)
streamlit run streamlit_app.py

# Dash (debug mode)
python app/app.py
```

## 📈 Performance

- ✅ Cached data loading
- ✅ Efficient pandas operations
- ✅ Optimized Plotly charts
- ✅ Responsive design (mobile-friendly)
- ✅ Fast filtering and calculations

## 🔒 Security Note

⚠️ **This is a DEMO application with sample data**

For production use, you should:

1. Add authentication (e.g., `streamlit-authenticator` or `dash-auth`)
2. Implement access controls
3. Use secure data sources (databases, APIs)
4. Enable HTTPS
5. Add data encryption
6. Implement audit logging
7. Remove demo data

## 🆚 Dash vs Streamlit - Which to Choose?

| Feature | Dash | Streamlit |
|---------|------|-----------|
| **Best For** | Complex dashboards | Quick deployment |
| **Hosting** | Requires server setup | Free on Streamlit Cloud |
| **Learning Curve** | Moderate (callbacks) | Easy (top-to-bottom) |
| **Interactivity** | Full control | Simple & fast |
| **Customization** | Highly customizable | Limited CSS control |
| **Performance** | Better for large apps | Great for small-medium |
| **Port** | 8051 | 8501 |

**Choose Streamlit** if you want to deploy quickly to the cloud for free!

**Choose Dash** if you need more control and customization.

## 🚀 Tech Stack

- **Frontend**: Streamlit or Dash
- **Charts**: Plotly
- **Data**: Pandas, NumPy
- **Language**: Python 3.10+

## 📝 License

See [LICENSE](LICENSE) file for details.

## 📧 Support

For issues or questions:
- Open a GitHub Issue
- Check the documentation in `README_STREAMLIT.md`

## ⚠️ Disclaimer

This dashboard displays **demo data** for demonstration purposes only. 

The information presented does not constitute investment advice and should not be used as the basis for any investment decision.

Past performance is not indicative of future results. All investments carry risk, including the potential loss of principal.

---

**Made with ❤️ for wealth management professionals**

🌟 **Star this repo** if you find it useful!
