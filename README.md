# H.A.R.C. System (Hydro Automated Retro Cannon)

A high-performance water-based weapon system featuring human tracking capabilities through multi-modal AI detection (Camera, LiDAR, Thermal).

> [!IMPORTANT]
> **Cross-Platform Support**: This application is fully compatible with both **Ubuntu (Linux)** and **Windows**.

## 🚀 Quick Start

The H.A.R.C. System uses a centralized management script (`manage.js`) to ensure consistent behavior across all operating systems.

### Installation & Startup

#### 🐧 On Ubuntu (Linux)
You can use the shell wrapper (requires execute permission) or run directly with Node:
```bash
# Recommended
node manage.js start

# Or using the wrapper
chmod +x install-run.sh
./install-run.sh
```

#### 🪟 On Windows
Use the PowerShell launchers (recommended) or the command prompt:
```powershell
# Recommended (PowerShell)
.\install-run.ps1

# Or using Node directly
node manage.js start
```

> [!NOTE]
> If you get a permission error in PowerShell, run: `Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process` before running the script.

## 🏗️ Project Structure (Zero-Root Architecture)

The project follows a strictly isolated architecture where all logic is contained within sub-directories, leaving the root clean for management scripts.

```
HARC/
├── backend/                # FASTApi (Python 3.8+)
│   ├── app/                # Core business logic & services
│   ├── ml/                 # Machine Learning models & data
│   ├── hardware_config.json # Device path configurations
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js (React) + Electron Wrapper
│   ├── src/                # UI Components & Web Logic
│   ├── electron/           # Desktop integration (Main/Preload)
│   ├── assets/             # Branding & Icons
│   └── package.json        # Main project orchestration
├── manage.js               # Universal Cross-Platform Manager
├── install-run.sh          # Linux startup wrapper
├── install-run.bat         # Windows startup wrapper
└── build.sh                # Linux distribution builder
```

## ✨ Core Features

- **Multi-Modal Tracking**: Real-time human detection across Camera feed, LiDAR point clouds, and Thermal imaging.
- **Auto-Targeting**: ML-based automated target selection and engagement system.
- **Weapon Control**: Precision motor control for water cannon positioning and pressure regulation.
- **Joystick Integration**: Support for physical joystick input for manual override.
- **System Vitals**: Real-time monitoring of CPU, GPU, and Hardware status.
- **Offline First**: No internet connection required. All AI processing happens locally.

## 🔧 Hardware Configuration

Device paths are managed in `backend/hardware_config.json`. 

> [!TIP]
> **Windows Users**: Use COM ports (e.g., `COM3`) for serial devices.
> **Linux Users**: Use device paths (e.g., `/dev/ttyUSB0`).

## ⚙️ Management Commands

You can interact with the system using `node manage.js [command]`:

| Command | Description |
| :--- | :--- |
| `install` | Sets up venv and installs all dependencies (Python & Node). |
| `start` | Automatically installs and launches the full system. |
| `build` | Packages the application into a standalone installer (`.AppImage`/`.deb` or `.exe`). |

## 📦 Building Distribution Packages

To create a standalone installer for your current platform:
```bash
node manage.js build
```
Output files will be generated in `frontend/dist/`.

## 📄 License
Private project - All rights reserved

---
**Version**: 1.1.0 (Zero-Root / Cross-Platform)
**Last Updated**: April 2026
