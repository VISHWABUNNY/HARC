# H.A.R.C. System (Hydro Automated Retro Cannon)

A water-based weapon system with human tracking capabilities using AI-powered detection. Runs as a standalone Ubuntu desktop application.

## 🚀 Quick Start

### Installation

**Option 1: Automated Install (Recommended)**
```bash
chmod +x install.sh
./install.sh
```

**Option 2: Manual Install**
```bash
# Install root dependencies
npm install

# Install backend dependencies
cd backend
./venv/bin/pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
cd ..
```

### Running the Application

**As Ubuntu Desktop App:**
```bash
npm run electron
# or
./harc-launcher.sh
```

**As Web Application (Development):**
```bash
npm run dev
```

This starts:
- Backend: http://localhost:8000
- Frontend: http://localhost:9002

## 📋 Prerequisites

- **Python 3.8+** (Python 3.12 recommended)
- **Node.js 18+** and npm
- **Ubuntu/Debian** Linux system
- **No internet connection required** - Fully offline operation

## 🏗️ Project Structure

```
HARC/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # API Routes
│   │   │   ├── tracking.py    # Human tracking endpoints
│   │   │   └── system.py      # System endpoints
│   │   ├── models/            # Pydantic Models
│   │   └── services/          # Business Logic
│   │       ├── ai_service.py
│   │       ├── system_service.py
│   │       ├── auto_targeting_service.py
│   │       ├── joystick_service.py
│   │       ├── motor_controller_service.py
│   │       └── joystick_motor_bridge.py
│   ├── hardware_config.json   # Hardware device configuration
│   ├── requirements.txt       # Python dependencies
│   └── run.py                 # Backend startup script
│
├── frontend/                  # Next.js Frontend
│   ├── src/
│   │   ├── app/               # Next.js App Router
│   │   ├── components/        # React Components
│   │   ├── lib/               # Utilities & API client
│   │   └── hooks/             # React hooks
│   └── package.json
│
├── electron/                  # Electron Desktop App
│   ├── main.js                # Main Electron process
│   └── preload.js             # Preload script
│
├── install.sh                 # Installation script
├── harc-launcher.sh           # Application launcher
├── build-app.sh               # Build distribution package
└── package.json               # Root package.json
```

## ✨ Features

- **Live Camera Human Tracking** - Real-time human detection from webcam feed
- **LiDAR Human Tracking** - Human detection from LiDAR point cloud data
- **Thermal Human Tracking** - Human detection from thermal imaging
- **Water Cannon Control** - Manual and AI-controlled water cannon system
- **Auto-Targeting Mode** - ML-based automated target selection and engagement
- **Joystick Control** - Physical joystick input for manual control
- **Motor Controller** - Serial communication with motor controller hardware
- **System Diagnostics** - Real-time monitoring of CPU, GPU, motor, and uptime
- **Real-time Monitoring** - Live system logs and status updates
- **Hardware Configuration** - JSON-based device path configuration

## 🔧 Hardware Configuration

Configure hardware devices in `backend/hardware_config.json`:

```json
{
  "camera": {
    "enabled": false,
    "path": "/dev/video0",
    "type": "v4l2"
  },
  "lidar": {
    "enabled": false,
    "path": "/dev/ttyUSB0",
    "type": "serial",
    "baudrate": 115200
  },
  "thermal": {
    "enabled": false,
    "path": "/dev/i2c-1",
    "type": "i2c",
    "address": "0x5A"
  },
  "water_pressure": {
    "enabled": false,
    "path": "/dev/ttyACM0",
    "type": "serial",
    "baudrate": 9600
  },
  "joystick": {
    "enabled": false,
    "path": "/dev/input/js0",
    "type": "linux_joystick"
  },
  "motor_controller": {
    "enabled": false,
    "path": "/dev/ttyUSB1",
    "type": "serial",
    "baudrate": 9600
  }
}
```

### Finding Device Paths

**Camera:**
```bash
ls -la /dev/video*
v4l2-ctl --list-devices
```

**Serial Devices (LiDAR, Motor Controller, Water Pressure):**
```bash
ls -la /dev/ttyUSB* /dev/ttyACM*
dmesg | grep -i tty
```

**I2C Devices (Thermal):**
```bash
ls -la /dev/i2c-*
i2cdetect -l
```

**Joystick:**
```bash
ls -la /dev/input/js*
cat /proc/bus/input/devices | grep -A 5 -i joystick
```

## 🔌 API Endpoints

### Tracking Endpoints
- `POST /api/tracking/camera` - Track humans from camera feed
- `POST /api/tracking/lidar` - Track humans from LiDAR data
- `POST /api/tracking/thermal` - Track humans from thermal imaging

### System Endpoints
- `GET /api/system/stats?aiMode={mode}` - Get system statistics
- `GET /api/system/vitals` - Get system vitals (CPU, GPU, motor, uptime)
- `GET /api/system/logs?category={category}&limit={limit}` - Get system logs
- `POST /api/system/logs?category={category}&message={message}` - Add system log
- `GET /api/system/weapon` - Get weapon status
- `PUT /api/system/weapon/pressure?pressure={value}` - Update water pressure
- `PUT /api/system/weapon/position?x={x}&y={y}` - Update cannon position
- `GET /api/system/status` - Get system online status
- `POST /api/system/auto-targeting/start` - Start auto-targeting mode
- `POST /api/system/auto-targeting/stop` - Stop auto-targeting mode
- `GET /api/system/auto-targeting/status` - Get auto-targeting status

### Utility Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Swagger API documentation

## ⚙️ Configuration

### Backend Environment Variables (.env)

Create `backend/.env` from `backend/env.example`:

```env
# OFFLINE MODE - No external API keys needed
PORT=8000  # Backend port
```

**Note:** The system runs in **OFFLINE MODE** by default. All AI features use local processing and do not require internet connectivity.

### Frontend Environment Variables (.env.local - optional)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🛠️ Development

### Backend Development
```bash
cd backend
./venv/bin/python run.py
```
- Auto-reloads on file changes
- API docs: http://localhost:8000/docs

### Frontend Development
```bash
cd frontend
npm run dev
```
- Hot-reloads on file changes
- Runs on: http://localhost:9002

### Run Both Together
```bash
npm run dev
```

## 📦 Building Distribution Package

Create standalone executable:

```bash
npm run build:electron
```

This creates:
- `dist/H.A.R.C. System-*.AppImage` - Portable executable
- `dist/H.A.R.C. System-*.deb` - Debian package

Or use the build script:
```bash
chmod +x build-app.sh
./build-app.sh
```

## 🐛 Troubleshooting

### Backend Issues

**Backend won't start:**
- Install dependencies: `cd backend && ./venv/bin/pip install -r requirements.txt`
- Check port availability: `lsof -i :8000`
- Verify Python version: `python3 --version` (needs 3.8+)

**Module not found:**
- Activate virtual environment: `source backend/venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

**Port already in use:**
- Change PORT in `backend/.env`
- Or kill process: `lsof -ti:8000 | xargs kill`

**API key error:**
- System runs in offline mode - no API keys needed

### Frontend Issues

**Frontend won't start:**
- Install dependencies: `cd frontend && npm install`
- Check backend is running: `curl http://localhost:8000/health`
- Verify Node.js version: `node --version` (needs 18+)

**Cannot connect to backend:**
- Check backend is running: `curl http://localhost:8000/health`
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`
- Check browser console for CORS errors

**Components showing "Loading..." indefinitely:**
- Backend is not running - start it: `cd backend && ./venv/bin/python run.py`
- API calls have 5-second timeout - check error messages

### Hardware Issues

**Device not found:**
- Check device path in `hardware_config.json`
- Verify device permissions: `ls -la /dev/video0` (should be readable)
- Add user to groups: `sudo usermod -a -G video,dialout,input $USER`
- Log out and back in for group changes to take effect

**Permission denied:**
- Check device permissions: `ls -la /dev/input/js0`
- May need to run with sudo (not recommended) or fix permissions
- For serial devices: `sudo chmod 666 /dev/ttyUSB0`

### Electron Issues

**Electron won't start:**
- Install Electron: `npm install electron electron-builder --save-dev`
- Check system libraries: May need `sudo apt install libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2`
- Verify Node.js version: `node --version` (needs 18+)

## 📚 Dependencies

### Backend (requirements.txt)
- `fastapi` - Web framework
- `uvicorn[standard]` - ASGI server
- `psutil` - System monitoring
- `pynvml` - GPU monitoring
- `python-evdev` - Joystick input
- `pyserial` - Serial communication
- `pillow` - Image processing
- `opencv-python` - Computer vision (offline AI processing)
- `numpy` - Numerical computing

**Note:** All dependencies are for local/offline processing. No external API calls are made.

### Frontend (package.json)
- `next` - React framework
- `react` - UI library
- `typescript` - Type safety
- `tailwindcss` - Styling
- `lucide-react` - Icons
- `@radix-ui/*` - UI components
- `recharts` - Charts

### Electron
- `electron` - Desktop framework
- `electron-builder` - Packaging tool

## 🌐 Access Points

- **Frontend Dashboard**: http://localhost:9002
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📝 System Modes

### Manual Mode
- User controls water cannon position and pressure manually
- Joystick input (if enabled) controls motor movement
- No automatic targeting

### Full Auto Mode
- ML-based auto-targeting service enabled
- Automatically selects targets based on scoring algorithm
- Automatically positions cannon and engages targets
- Processes camera feed for human detection

## 🔄 Data Flow

1. **User Action** → Frontend component
2. **API Call** → `src/lib/api.ts` (with 5-second timeout)
3. **HTTP Request** → Backend FastAPI endpoint
4. **Processing** → Service layer (AI, System, Hardware)
5. **AI Analysis** → Local offline processing (OpenCV, local algorithms)
6. **Hardware I/O** → Device communication (if enabled)
7. **Response** → Pydantic models → JSON
8. **Display** → Frontend renders results

**All processing is done locally - no internet connection required.**

## 📄 License

Private project - All rights reserved

---

**Version**: 1.0.0  
**Last Updated**: December 2024
