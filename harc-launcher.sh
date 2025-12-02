#!/bin/bash

# H.A.R.C. System Launcher
# Starts the Electron application

cd "$(dirname "$0")"

# Check if Electron is installed
if ! command -v electron &> /dev/null; then
    echo "❌ Electron not found. Installing dependencies..."
    npm install
fi

# Start Electron app
npm run electron

