# Deployment Guide - Streamlit Cloud

## 🎯 Prerequisites

- [ ] GitHub account
- [ ] This repository forked/cloned to your GitHub
- [ ] Streamlit Cloud account (free - sign up at [streamlit.io/cloud](https://streamlit.io/cloud))

## 📋 Deployment Checklist

### Step 1: Prepare Your Repository

- [ ] Ensure `streamlit_app.py` is in the root directory
- [ ] Ensure `requirements_streamlit.txt` exists
- [ ] Ensure `.streamlit/config.toml` exists
- [ ] All data files are in `app/data/` directory
- [ ] Push all changes to GitHub

### Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Navigate to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub

2. **Create New App**
   - Click "New app" button
   - Or go directly to: [share.streamlit.io/deploy](https://share.streamlit.io/deploy)

3. **Configure App Settings**
   ```
   Repository: your-username/trust_found_demo
   Branch: main
   Main file path: streamlit_app.py
   ```

4. **Advanced Settings** (click "Advanced settings")
   ```
   Python version: 3.10
   Requirements file: requirements_streamlit.txt
   ```

5. **Deploy!**
   - Click "Deploy" button
   - Wait 2-3 minutes for initial deployment
   - Your app will be available at: `https://your-app-name.streamlit.app`

### Step 3: Verify Deployment

- [ ] App loads without errors
- [ ] All tabs are accessible
- [ ] Charts render correctly
- [ ] Filters work properly
- [ ] Data tables display
- [ ] Language toggle works
- [ ] Currency conversion works

## 🔧 Troubleshooting

### Common Issues

#### App Won't Start

**Problem**: "ModuleNotFoundError"
**Solution**: Ensure `requirements_streamlit.txt` includes all dependencies:
```txt
streamlit==1.31.0
plotly==5.18.0
pandas==2.1.4
numpy==1.26.2
```

#### Data Not Loading

**Problem**: "FileNotFoundError" for CSV/JSON files
**Solution**: 
- Ensure `app/data/` directory is committed to GitHub
- Check file paths in `app/services/data_loader.py`
- Verify all data files are present

#### Charts Not Displaying

**Problem**: Blank chart areas
**Solution**:
- Check browser console for errors
- Ensure plotly version matches requirements
- Try clearing browser cache

#### App Crashes on Tab Switch

**Problem**: App crashes when changing tabs
**Solution**:
- Check for missing data in filtered datasets
- Add data validation in tab rendering functions
- Review Streamlit logs in cloud dashboard

### View Logs

1. Go to Streamlit Cloud dashboard
2. Click on your app
3. Click "Manage app"
4. View logs in the "Logs" section

## 🎨 Customization After Deployment

### Update Theme Colors

Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#1a365d"     # Your brand color
backgroundColor = "#f8fafc"  # Background
secondaryBackgroundColor = "#ffffff"  # Cards
textColor = "#1a202c"        # Text
```

Push changes to GitHub - Streamlit will auto-redeploy!

### Update Data

1. Replace files in `app/data/` directory
2. Commit and push to GitHub
3. App will automatically redeploy with new data

### Add Custom Domain

Streamlit Cloud free tier uses:
- `https://your-app-name.streamlit.app`

For custom domains:
- Upgrade to Streamlit Cloud Teams or Business plan
- Or use a reverse proxy (e.g., Cloudflare, nginx)

## 🔒 Adding Authentication

### Option 1: Streamlit-Authenticator

1. Install package:
```bash
pip install streamlit-authenticator
```

2. Add to `requirements_streamlit.txt`:
```txt
streamlit-authenticator==0.2.3
```

3. Add auth code to `streamlit_app.py`:
```python
import streamlit_authenticator as stauth

# Configure authenticator
names = ['John Smith', 'Rebecca Briggs']
usernames = ['jsmith', 'rbriggs']
passwords = ['abc', 'def']  # Use hashed passwords in production!

authenticator = stauth.Authenticate(
    names, usernames, passwords,
    'sqn_trust_dashboard', 'auth_cookie', cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    # Your dashboard code here
    authenticator.logout('Logout', 'sidebar')
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
```

### Option 2: Streamlit Secrets for API Keys

If your app needs API keys or database credentials:

1. Go to Streamlit Cloud dashboard
2. Click "Settings" for your app
3. Navigate to "Secrets" section
4. Add secrets in TOML format:
```toml
[database]
host = "your-db-host"
username = "your-username"
password = "your-password"

[api]
key = "your-api-key"
```

5. Access in code:
```python
import streamlit as st

db_host = st.secrets["database"]["host"]
api_key = st.secrets["api"]["key"]
```

## 📊 Monitoring & Analytics

### Built-in Streamlit Analytics

Streamlit Cloud provides:
- ✅ App visitor count
- ✅ Resource usage (CPU, memory)
- ✅ Error logs
- ✅ Deployment history

Access via: App Dashboard → Analytics

### Add Google Analytics (Optional)

1. Create Google Analytics property
2. Add tracking code to `streamlit_app.py`:

```python
import streamlit.components.v1 as components

# Google Analytics
GA_TRACKING_ID = "UA-XXXXXXXXX-X"

ga_code = f"""
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_TRACKING_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_TRACKING_ID}');
</script>
"""

components.html(ga_code)
```

## 🚀 Performance Optimization

### Enable Caching

Ensure data loading functions use `@st.cache_data`:

```python
import streamlit as st

@st.cache_data
def load_holdings():
    return pd.read_csv("app/data/holdings.csv")
```

### Optimize Large Datasets

For datasets >10MB:
1. Use `st.cache_data` decorator
2. Filter data early in the pipeline
3. Use parquet instead of CSV
4. Implement pagination for tables

### Resource Limits (Free Tier)

Streamlit Cloud Free tier:
- 1 GB RAM
- 1 CPU core
- 1 GB storage

If you exceed limits:
- Optimize data loading
- Reduce chart complexity
- Implement lazy loading
- Upgrade to paid tier

## 🔄 Continuous Deployment

### Auto-Deploy on Git Push

Streamlit Cloud automatically redeploys when you:
1. Push to the connected GitHub repository
2. On the connected branch (usually `main`)

### Manual Reboot

Sometimes needed after:
- Changing secrets
- Modifying config files
- Debugging issues

To manually reboot:
1. Go to app dashboard
2. Click "⋮" menu
3. Select "Reboot app"

## 📱 Mobile Optimization

The Streamlit version is mobile-responsive, but test on:
- [ ] iPhone (Safari)
- [ ] Android (Chrome)
- [ ] Tablet (iPad)

Tips for mobile:
- Use `st.columns()` for responsive layouts
- Keep charts simple
- Use expanders for large content
- Test filter controls on small screens

## 🎉 You're Live!

Your dashboard is now deployed and accessible worldwide! 🌍

**Share your app:**
- URL: `https://your-app-name.streamlit.app`
- QR Code: Generate at [qr-code-generator.com](https://www.qr-code-generator.com/)

**Next Steps:**
1. Share with stakeholders
2. Gather feedback
3. Iterate and improve
4. Monitor usage and performance

## 📞 Need Help?

- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **Community Forum**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **GitHub Issues**: Open an issue in this repository

---

Happy deploying! 🚀
