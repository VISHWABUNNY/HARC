#!/bin/bash

echo "🔧 Setting up H.A.R.C. Backend..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Check if venv already exists
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists."
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing virtual environment..."
        rm -rf venv
    else
        echo "✅ Using existing virtual environment."
        exit 0
    fi
fi

# Try to create virtual environment
echo "📦 Creating virtual environment..."
if python3 -m venv venv 2>/dev/null; then
    echo "✅ Virtual environment created successfully!"
else
    echo "❌ Failed to create virtual environment."
    echo ""
    echo "On Debian/Ubuntu systems, you need to install python3-venv:"
    echo "  sudo apt install python3-venv"
    echo ""
    echo "Or use virtualenv instead:"
    echo "  pip install virtualenv"
    echo "  virtualenv venv"
    exit 1
fi

# Activate and install dependencies
echo ""
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run the backend:"
echo "  python run.py"
echo ""

