#!/bin/bash

# H.A.R.C. System - Combined Install & Run Script (Restructured)
# This script ensures dependencies are installed and then runs the application.

set -e

echo "🚀 H.A.R.C. System - Startup"
echo "============================="

# 0. Cleanup any zombie processes
echo "🧹 Cleaning up old processes..."
pkill -f "next dev" || true
pkill -f "python3 run.py" || true
pkill -f "electron" || true

# 1. Check & Install System Dependencies
if ! command -v npm &> /dev/null || ! command -v python3 &> /dev/null; then
    echo "📦 System dependencies missing. Running installer..."
    if [ "$EUID" -ne 0 ] && [ -f /usr/bin/apt-get ]; then
        echo "🔐 Sudo access required to install system packages."
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv nodejs npm build-essential libnss3-dev libatk-bridge2.0-dev libdrm2 libxkbcommon-dev libxcomposite-dev libxdamage-dev libxrandr-dev libgbm-dev libasound2-dev
    fi
fi

# 2. Install Backend Dependencies
if [ ! -d "backend/venv" ]; then
    echo "🐍 Setting up Python virtual environment..."
    cd backend
    python3 -m venv venv
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install -r requirements.txt
    cd ..
fi

# 3. Install Frontend & Orchestration Dependencies
if [ ! -d "frontend/node_modules" ] || [ ! -f "frontend/node_modules/.bin/next" ]; then
    echo "⚛️  Installing frontend and orchestration dependencies..."
    cd frontend
    npm install
    cd ..
fi

# 4. Build frontend if it hasn't been built yet
if [ ! -d "frontend/.next" ]; then
    echo "🔨 Building frontend for the first time..."
    cd frontend
    npm run build
    cd ..
fi

# 5. Launch Application
echo "🎯 Starting H.A.R.C. System..."
cd frontend
npm run electron:start
