#!/bin/bash

# Build H.A.R.C. System as Ubuntu Desktop Application

set -e

echo "🔨 Building H.A.R.C. System as Ubuntu Desktop App"
echo "=================================================="
echo ""

# Check dependencies
if ! command -v electron-builder &> /dev/null; then
    echo "📦 Installing electron-builder..."
    npm install -g electron-builder
fi

# Build frontend
echo "📦 Building frontend..."
cd frontend
npm run build
cd ..

# Build Electron app
echo "📦 Building Electron application..."
npm run build:electron

echo ""
echo "✅ Build complete!"
echo ""
echo "📦 Output files:"
echo "   - dist/H.A.R.C. System-*.AppImage (Portable)"
echo "   - dist/H.A.R.C. System-*.deb (Debian package)"
echo ""
echo "💡 To install:"
echo "   sudo dpkg -i dist/H.A.R.C.\\ System-*.deb"
echo "   # or"
echo "   chmod +x dist/H.A.R.C.\\ System-*.AppImage"
echo "   ./dist/H.A.R.C.\\ System-*.AppImage"
echo ""

