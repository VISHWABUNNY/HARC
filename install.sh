#!/bin/bash

# H.A.R.C. System Installation Script for Ubuntu

set -e

echo "🚀 H.A.R.C. System - Ubuntu Installation"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "❌ Please do not run as root. Run as regular user."
   exit 1
fi

# Check Ubuntu/Debian
if ! command -v apt-get &> /dev/null; then
    echo "❌ This script is for Ubuntu/Debian systems only."
    exit 1
fi

echo "📦 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    build-essential \
    libnss3-dev \
    libatk-bridge2.0-dev \
    libdrm2 \
    libxkbcommon-dev \
    libxcomposite-dev \
    libxdamage-dev \
    libxrandr-dev \
    libgbm-dev \
    libasound2-dev

echo ""
echo "✅ System dependencies installed"
echo ""

# Install project dependencies
echo "📥 Installing project dependencies..."

# Install root dependencies (Electron)
npm install

# Install backend dependencies
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
cd ..

# Install frontend dependencies
cd frontend
npm install
cd ..

echo ""
echo "✅ Project dependencies installed"
echo ""

# Create desktop entry
echo "🖥️  Creating desktop application entry..."

DESKTOP_FILE="$HOME/.local/share/applications/harc-system.desktop"
mkdir -p "$HOME/.local/share/applications"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=H.A.R.C. System
Comment=Hydro Automated Retro Cannon - Water-based weapon system with human tracking
Exec=$(pwd)/harc-launcher.sh
Icon=$(pwd)/assets/icon.png
Terminal=false
Categories=Utility;Security;
Keywords=weapon;tracking;cannon;security;
EOF

chmod +x "$DESKTOP_FILE"

echo "✅ Desktop entry created: $DESKTOP_FILE"
echo ""

# Create launcher script
echo "📝 Creating launcher script..."

LAUNCHER_SCRIPT="$(pwd)/harc-launcher.sh"

cat > "$LAUNCHER_SCRIPT" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
npm run electron
EOF

chmod +x "$LAUNCHER_SCRIPT"

echo "✅ Launcher script created: $LAUNCHER_SCRIPT"
echo ""

# Build frontend for production
echo "🔨 Building frontend for production..."
cd frontend
npm run build
cd ..

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Next Steps:"
echo "   1. Find 'H.A.R.C. System' in your applications menu"
echo "   2. Or run: npm run electron"
echo "   3. Or run: ./harc-launcher.sh"
echo ""
echo "🎯 The application will start both backend and frontend automatically!"
echo ""

