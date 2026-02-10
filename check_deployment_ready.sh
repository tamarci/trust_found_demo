#!/bin/bash

# Deployment Readiness Checker
echo "🔍 Checking if your app is ready for Streamlit Cloud deployment..."
echo "=================================================================="
echo ""

errors=0
warnings=0

# Check 1: Required files exist
echo "📁 Checking required files..."
if [ -f "streamlit_app.py" ]; then
    echo "  ✅ streamlit_app.py found"
else
    echo "  ❌ streamlit_app.py NOT FOUND"
    ((errors++))
fi

if [ -f "requirements_streamlit.txt" ]; then
    echo "  ✅ requirements_streamlit.txt found"
else
    echo "  ❌ requirements_streamlit.txt NOT FOUND"
    ((errors++))
fi

if [ -f ".streamlit/config.toml" ]; then
    echo "  ✅ .streamlit/config.toml found"
else
    echo "  ⚠️  .streamlit/config.toml NOT FOUND (optional but recommended)"
    ((warnings++))
fi

if [ -d "app/data" ]; then
    echo "  ✅ app/data directory found"
    data_files=$(ls app/data/*.csv app/data/*.json 2>/dev/null | wc -l)
    echo "     Found $data_files data files"
else
    echo "  ❌ app/data directory NOT FOUND"
    ((errors++))
fi

echo ""

# Check 2: No Dash imports in streamlit_app.py
echo "🔍 Checking for Dash dependencies..."
if grep -q "from dash import\|import dash" streamlit_app.py 2>/dev/null; then
    echo "  ❌ Found Dash imports in streamlit_app.py!"
    echo "     This will cause deployment to fail."
    ((errors++))
else
    echo "  ✅ No Dash imports found"
fi

echo ""

# Check 3: Requirements file content
echo "📦 Checking requirements_streamlit.txt..."
if [ -f "requirements_streamlit.txt" ]; then
    if grep -q "dash" requirements_streamlit.txt; then
        echo "  ⚠️  Found 'dash' in requirements - should only be in requirements.txt"
        ((warnings++))
    else
        echo "  ✅ No Dash in requirements (correct!)"
    fi
    
    if grep -q "streamlit" requirements_streamlit.txt; then
        echo "  ✅ Streamlit is listed"
    else
        echo "  ❌ Streamlit not found in requirements!"
        ((errors++))
    fi
fi

echo ""

# Check 4: Git status
echo "📊 Checking git status..."
if command -v git &> /dev/null; then
    if git rev-parse --git-dir > /dev/null 2>&1; then
        uncommitted=$(git status --porcelain | wc -l | tr -d ' ')
        if [ "$uncommitted" -gt 0 ]; then
            echo "  ⚠️  You have $uncommitted uncommitted changes"
            echo "     Run: git add . && git commit -m 'message' && git push"
            ((warnings++))
        else
            echo "  ✅ All changes committed"
        fi
        
        unpushed=$(git log origin/$(git rev-parse --abbrev-ref HEAD)..HEAD 2>/dev/null | wc -l | tr -d ' ')
        if [ "$unpushed" -gt 0 ]; then
            echo "  ⚠️  You have unpushed commits"
            echo "     Run: git push origin main"
            ((warnings++))
        else
            echo "  ✅ All commits pushed"
        fi
    else
        echo "  ⚠️  Not a git repository"
        ((warnings++))
    fi
else
    echo "  ⚠️  Git not installed"
    ((warnings++))
fi

echo ""

# Check 5: Test imports
echo "🧪 Testing Python imports..."
if command -v python3 &> /dev/null; then
    if [ -f "test_imports.py" ]; then
        # Capture only the summary
        test_output=$(python3 test_imports.py 2>&1)
        if echo "$test_output" | grep -q "ALL TESTS PASSED"; then
            echo "  ✅ All imports working"
        elif echo "$test_output" | grep -q "No module named 'streamlit'"; then
            # Streamlit not installed locally is OK - check if app modules work
            if echo "$test_output" | grep -q "✅ app.services.data_loader" && \
               echo "$test_output" | grep -q "✅ app.components.charts" && \
               echo "$test_output" | grep -q "✅ Data loading works"; then
                echo "  ✅ App modules working (Streamlit not installed locally, but that's OK)"
            else
                echo "  ❌ Import test failed"
                echo "$test_output" | tail -10
                ((errors++))
            fi
        else
            echo "  ❌ Import test failed"
            echo "$test_output" | tail -10
            ((errors++))
        fi
    else
        echo "  ⚠️  test_imports.py not found (run test manually)"
        ((warnings++))
    fi
else
    echo "  ⚠️  Python3 not found"
    ((warnings++))
fi

echo ""
echo "=================================================================="
echo "📊 SUMMARY"
echo "=================================================================="
echo ""

if [ $errors -eq 0 ] && [ $warnings -eq 0 ]; then
    echo "🎉 PERFECT! Your app is ready to deploy!"
    echo ""
    echo "Next steps:"
    echo "  1. Go to https://share.streamlit.io"
    echo "  2. Click 'New app'"
    echo "  3. Configure:"
    echo "     - Main file: streamlit_app.py"
    echo "     - Python: 3.10"
    echo "     - Requirements: requirements_streamlit.txt"
    echo "  4. Click Deploy!"
    echo ""
    exit 0
elif [ $errors -eq 0 ]; then
    echo "✅ Ready to deploy (with $warnings warning(s))"
    echo ""
    echo "Warnings won't prevent deployment but should be fixed:"
    echo "- Commit and push any changes"
    echo "- Add missing optional files"
    echo ""
    exit 0
else
    echo "❌ NOT READY - Fix $errors error(s) first!"
    echo ""
    echo "Required fixes:"
    echo "- Add missing files"
    echo "- Remove Dash dependencies"  
    echo "- Fix import errors"
    echo ""
    echo "See TROUBLESHOOTING.md for detailed help"
    echo ""
    exit 1
fi
