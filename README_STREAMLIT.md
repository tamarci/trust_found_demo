# SQN Trust Portfolio Dashboard - Streamlit Version

A premium wealth management dashboard for portfolio visualization and analysis, built with Streamlit.

## Features

- 📊 **Portfolio Summary** - Real-time portfolio value, returns, and performance metrics
- 💼 **Asset Management** - Detailed asset breakdown with sector and region analysis
- 🏢 **Ownership Structure** - Company ownership visualization with Sankey diagrams
- 🗺️ **Real Estate Mapping** - Interactive maps showing property locations
- 🌍 **Diversity Analysis** - Portfolio diversity across sectors, regions, and risk levels
- 💡 **AI Insights** - Auto-generated portfolio insights and recommendations
- 📈 **Reports & Export** - CSV export and PDF report generation
- 🌐 **Multi-language** - English and Hungarian support
- 💱 **Multi-currency** - EUR, USD, and HUF support

## Installation

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd trust_found_demo
```

2. Install dependencies:
```bash
pip install -r requirements_streamlit.txt
```

3. Run the application:
```bash
streamlit run streamlit_app.py
```

The dashboard will be available at `http://localhost:8501`

## Deployment to Streamlit Cloud

### Quick Deploy

1. **Fork this repository** to your GitHub account

2. **Go to [Streamlit Cloud](https://streamlit.io/cloud)**

3. **Click "New app"**

4. **Configure your app:**
   - Repository: `your-username/trust_found_demo`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
   - Python version: 3.10

5. **Advanced settings:**
   - Requirements file: `requirements_streamlit.txt`

6. **Click "Deploy"**

Your app will be live at: `https://your-app-name.streamlit.app`

### Environment Variables

No environment variables are required for the demo version. All data is included in the repository.

## Project Structure

```
trust_found_demo/
├── streamlit_app.py          # Main Streamlit application
├── app/
│   ├── components/            # Reusable UI components
│   │   ├── charts.py         # Chart components
│   │   ├── tables.py         # Table components
│   │   ├── kpi_cards.py      # KPI card components
│   │   └── layout.py         # Layout utilities
│   ├── services/             # Business logic
│   │   ├── data_loader.py    # Data loading functions
│   │   ├── filters.py        # Data filtering
│   │   ├── metrics.py        # Metric calculations
│   │   └── translations.py   # i18n support
│   └── data/                 # Demo data
│       ├── accounts.csv
│       ├── holdings.csv
│       ├── nav.csv
│       ├── transactions.csv
│       ├── client.json
│       ├── ownership.json
│       └── real_estate_locations.json
├── .streamlit/
│   └── config.toml           # Streamlit configuration
└── requirements_streamlit.txt # Python dependencies
```

## Data

This dashboard uses demo data for demonstration purposes. The data includes:

- **Holdings**: Stock, real estate, and liquid asset positions
- **NAV History**: Historical net asset value data
- **Transactions**: Buy/sell transaction history
- **Ownership**: Company ownership structures
- **Real Estate**: Property locations and details

## Customization

### Theme

Edit `.streamlit/config.toml` to customize colors and appearance:

```toml
[theme]
primaryColor = "#1a365d"
backgroundColor = "#f8fafc"
secondaryBackgroundColor = "#ffffff"
textColor = "#1a202c"
```

### Data

Replace the CSV and JSON files in `app/data/` with your own data following the same schema.

## Technical Stack

- **Framework**: Streamlit
- **Visualization**: Plotly
- **Data Processing**: Pandas, NumPy
- **Languages**: Python 3.10+

## Performance

- Cached data loading for fast page loads
- Efficient filtering and calculations
- Responsive design for mobile and desktop

## Security

⚠️ **Important**: This is a demo application with sample data. For production use:

1. Add authentication (e.g., `streamlit-authenticator`)
2. Implement proper access controls
3. Use secure data sources (databases, APIs)
4. Enable HTTPS
5. Add data encryption
6. Implement audit logging

## Support

For issues or questions, please open an issue on GitHub.

## License

See LICENSE file for details.

## Disclaimer

This dashboard displays demo data generated for demonstration purposes only. The information presented does not constitute investment advice and should not be used as the basis for any investment decision.

Past performance is not indicative of future results. All investments carry risk, including the potential loss of principal.
