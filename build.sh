#!/bin/bash

# H.A.R.C. System - Distribution Build Script (Restructured)
# This script packages the application into standalone AppImage and DEB files.

set -e

echo "🔨 Building H.A.R.C. System Release"
echo "==================================="

# 1. Ensure dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing build dependencies in frontend..."
    cd frontend
    npm install
    cd ..
fi

# 2. Build Frontend and Desktop App
echo "⚛️  Building and packaging from frontend directory..."
cd frontend
npm run build
npm run build:electron
cd ..

echo ""
echo "✅ Build complete!"
echo "📦 Output files can be found in 'frontend/dist/'."
