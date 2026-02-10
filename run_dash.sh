#!/bin/bash

# SQN Trust Portfolio Dashboard - Dash Launcher
# This script sets up and runs the Dash version

echo "🏦 SQN Trust Portfolio Dashboard - Dash Version"
echo "=================================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
echo "📥 Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✓ All dependencies installed"
echo ""

# Run Dash app
echo "🚀 Starting Dash server..."
echo "📱 Access the dashboard at: http://localhost:8051"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app/app.py

# Deactivate virtual environment on exit
deactivate
