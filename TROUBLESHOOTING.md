# Troubleshooting Guide - Streamlit Cloud Deployment

## 🔥 Common Deployment Issues

### Issue 1: Build Takes More Than 10 Minutes

**Symptoms:**
- App shows "Your app is in the oven" for >10 minutes
- Build seems stuck
- No error messages visible

**Causes & Solutions:**

#### A. Missing or Incorrect Requirements

**Problem:** `requirements_streamlit.txt` is missing dependencies or has wrong versions

**Solution:**
```bash
# Verify requirements file exists
ls -la requirements_streamlit.txt

# Should contain:
streamlit==1.31.0
plotly==5.18.0
pandas==2.1.4
numpy==1.26.2
```

**Fix:** Make sure you specified `requirements_streamlit.txt` in Advanced Settings, not `requirements.txt` (which has Dash dependencies)

#### B. Import Errors (Most Common!)

**Problem:** Code imports Dash components that aren't in Streamlit requirements

**Solution:**
```bash
# Run the test script locally first
python3 test_imports.py
```

This will catch import errors before deploying.

**Common import issues:**
- ❌ `from dash import html, dcc` → Not compatible with Streamlit
- ❌ `import dash_bootstrap_components` → Not needed for Streamlit
- ✅ `import streamlit as st` → Correct
- ✅ `import plotly.graph_objects as go` → Correct

#### C. Large Files in Repository

**Problem:** Repo has large files (>100MB) that slow down build

**Solution:**
```bash
# Check for large files
find . -type f -size +10M -not -path "*/venv/*" -not -path "*/.git/*"

# Remove large files from git history if needed
git filter-branch --tree-filter 'rm -f path/to/large/file' HEAD
```

**Streamlit Cloud limits:**
- Free tier: 1GB RAM, 1GB storage
- Keep data files <50MB for best performance

#### D. Python Version Mismatch

**Problem:** Code uses Python 3.11+ features but Streamlit Cloud uses 3.10

**Solution:**
- Check Advanced Settings → Python version: should be 3.10
- Avoid using match/case statements (Python 3.10+)
- Don't use TypeScript-style type hints

#### E. Data Files Not Found

**Problem:** CSV/JSON files missing or wrong path

**Solution:**
```bash
# Verify all data files are committed
git status
git add app/data/*
git commit -m "Add data files"
git push
```

**Check paths in data_loader.py:**
```python
# Should be:
DATA_DIR = Path(__file__).parent.parent / "data"  # Correct

# Not:
DATA_DIR = "/absolute/path/to/data"  # Wrong!
```

### Issue 2: App Builds But Crashes on Load

**Symptoms:**
- Build completes successfully
- App shows error page when you try to access it
- Logs show Python errors

**Solutions:**

#### Check Streamlit Cloud Logs

1. Go to Streamlit Cloud dashboard
2. Click your app
3. Click "Manage app"
4. View "Logs" tab
5. Look for error messages (usually at the bottom)

#### Common Runtime Errors:

**FileNotFoundError:**
```python
# Problem: Absolute paths
DATA_DIR = "/Users/you/project/data"

# Solution: Relative paths
DATA_DIR = Path(__file__).parent.parent / "data"
```

**ModuleNotFoundError:**
```python
# Problem: Missing package
from some_package import something

# Solution: Add to requirements_streamlit.txt
some_package==1.0.0
```

**AttributeError with st:**
```python
# Problem: Using Dash components
dbc.Card(...)

# Solution: Use Streamlit components
st.container()
```

### Issue 3: App Works Locally But Not on Cloud

**Possible causes:**

#### A. Environment Differences

**Local:**
```bash
# You might have installed extra packages globally
pip list | wc -l  # Shows 200+ packages
```

**Cloud:**
```bash
# Only installs packages in requirements_streamlit.txt
```

**Solution:** Test in a clean virtual environment:
```bash
# Create fresh venv
python3 -m venv test_env
source test_env/bin/activate

# Install ONLY requirements_streamlit.txt
pip install -r requirements_streamlit.txt

# Test imports
python3 test_imports.py

# Try running app
streamlit run streamlit_app.py
```

#### B. Case-Sensitive Paths

**Problem:** macOS/Windows are case-insensitive, Linux (Streamlit Cloud) is case-sensitive

```python
# Works locally (macOS):
from app.Services.data_loader import load_client  # ❌

# Works on cloud (Linux):
from app.services.data_loader import load_client  # ✅
```

**Solution:** Always use correct case for imports and file paths

#### C. Hidden Dependencies

**Problem:** Code uses packages not in requirements

```python
# This works if you have it installed locally:
import sklearn  # ❌ Not in requirements_streamlit.txt!
```

**Solution:**
1. Run `python3 test_imports.py` in clean venv
2. Add missing packages to requirements_streamlit.txt

## 🛠️ Debugging Steps

### Step 1: Test Locally in Clean Environment

```bash
# 1. Create clean virtual environment
rm -rf test_venv
python3 -m venv test_venv
source test_venv/bin/activate

# 2. Install only Streamlit requirements
pip install -r requirements_streamlit.txt

# 3. Run import test
python3 test_imports.py

# 4. If tests pass, try running the app
streamlit run streamlit_app.py

# 5. If app works, you're ready to deploy!
deactivate
```

### Step 2: Check Git Repository

```bash
# Verify all required files are committed
git status

# Should show no uncommitted changes to these files:
# - streamlit_app.py
# - requirements_streamlit.txt
# - .streamlit/config.toml
# - app/data/*.csv
# - app/data/*.json
# - app/services/*.py
# - app/components/*.py

# If files are missing:
git add .
git commit -m "Add missing files"
git push
```

### Step 3: Verify Streamlit Cloud Settings

Go to your app settings and verify:

```
✅ Repository: correct-username/trust_found_demo
✅ Branch: main (or your deployment branch)
✅ Main file path: streamlit_app.py
✅ Python version: 3.10
✅ Requirements file: requirements_streamlit.txt  ← IMPORTANT!
```

### Step 4: Check Requirements File Content

```bash
cat requirements_streamlit.txt
```

Should ONLY contain:
```
streamlit==1.31.0
plotly==5.18.0
pandas==2.1.4
numpy==1.26.2
```

Should NOT contain:
- ❌ dash
- ❌ dash-bootstrap-components
- ❌ gunicorn (only needed for Dash/Flask)

### Step 5: Monitor Build Logs

While deploying:
1. Keep Streamlit Cloud dashboard open
2. Watch the build logs in real-time
3. Look for:
   - "Collecting streamlit" ← Should appear quickly
   - "Installing collected packages" ← Should complete
   - "You can now view your Streamlit app" ← Success!

If stuck at "Collecting" for >5 minutes → Dependency resolution issue

## 🚨 Emergency Fixes

### Fix 1: Force Rebuild

Sometimes Streamlit Cloud cache gets stuck:

1. Go to app dashboard
2. Click "⋮" menu
3. Select "Reboot app"
4. Wait 2-3 minutes

### Fix 2: Delete and Redeploy

If reboot doesn't work:

1. Delete the app from Streamlit Cloud
2. Wait 5 minutes
3. Deploy fresh from GitHub

### Fix 3: Create Minimal Test App

Create `test_app.py`:
```python
import streamlit as st
st.write("Hello World!")
```

Deploy this first to verify Streamlit Cloud is working, then gradually add your code back.

## 📞 Still Stuck?

1. **Check Streamlit Community Forum:**
   - [discuss.streamlit.io](https://discuss.streamlit.io)
   - Search for your error message

2. **Check Status Page:**
   - [status.streamlit.io](https://status.streamlit.io)
   - Verify Streamlit Cloud is operational

3. **Enable Verbose Logging:**
   Add to streamlit_app.py:
   ```python
   import streamlit as st
   import logging
   
   logging.basicConfig(level=logging.DEBUG)
   st.write("App loaded successfully!")
   ```

4. **Test Specific Components:**
   Comment out sections of your app one by one to isolate the problem:
   ```python
   # Comment out tabs you're not testing
   # with tab2:
   #     # Complex code here
   #     pass
   ```

## ✅ Pre-Deployment Checklist

Before deploying, verify:

- [ ] Run `python3 test_imports.py` → All tests pass
- [ ] Run app locally with clean venv → Works perfectly
- [ ] All data files committed to git
- [ ] requirements_streamlit.txt is correct
- [ ] No Dash imports in code
- [ ] Python version set to 3.10 in Streamlit Cloud
- [ ] Requirements file path is `requirements_streamlit.txt`

---

**Last Resort:** Open an issue in this repository with:
1. Error message from Streamlit Cloud logs
2. Output of `python3 test_imports.py`
3. Screenshot of Streamlit Cloud settings
