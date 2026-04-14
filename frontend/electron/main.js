const { app, BrowserWindow, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow;
let backendProcess;
let frontendProcess;

// Paths - Updated for new location in frontend/electron/
const BACKEND_DIR = path.join(__dirname, '..', '..', 'backend');
const FRONTEND_DIR = path.join(__dirname, '..');
const BACKEND_SCRIPT = path.join(BACKEND_DIR, 'run.py');
const FRONTEND_SCRIPT = path.join(FRONTEND_DIR, 'node_modules', '.bin', 'next');

function createWindow() {
  // Create the browser window
  const iconPath = path.join(__dirname, '..', '..', 'assets', 'icon.png');
  const hasIcon = fs.existsSync(iconPath);
  
  mainWindow = new BrowserWindow({
    width: 1920,
    height: 1080,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: true
    },
    icon: hasIcon ? iconPath : undefined,
    titleBarStyle: 'default',
    show: false, // Don't show until ready
    autoHideMenuBar: false,
    backgroundColor: '#000000'
  });

  // Prevent navigation to external URLs
  mainWindow.webContents.on('will-navigate', (event, url) => {
    if (!url.startsWith('http://localhost:9002') && !url.startsWith('http://127.0.0.1:9002')) {
      event.preventDefault();
    }
  });

  // Prevent new window creation (browser opening)
  mainWindow.webContents.setWindowOpenHandler(() => {
    return { action: 'deny' };
  });

  // Start backend server first
  startBackend();

  // Wait for backend to be ready, then start frontend
  waitForBackend(() => {
    startFrontend();
    
    // Load frontend after it starts
    waitForFrontend(() => {
      mainWindow.loadURL('http://localhost:9002');
      mainWindow.show();
      
      // Open DevTools in development
      if (process.env.NODE_ENV === 'development') {
        mainWindow.webContents.openDevTools();
      }
    });
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Create application menu
  createMenu();
}

function checkBackendRunning(callback) {
  const http = require('http');
  const req = http.get('http://localhost:8000/health', (res) => {
    if (res.statusCode === 200) {
      console.log('Backend is already running');
      callback(true);
    } else {
      callback(false);
    }
  });
  
  req.on('error', () => {
    callback(false);
  });
  
  req.setTimeout(1000, () => {
    req.destroy();
    callback(false);
  });
}

function startBackend() {
  // Check if backend is already running
  checkBackendRunning((isRunning) => {
    if (isRunning) {
      console.log('Using existing backend server');
      return;
    }
    
    console.log('Starting backend server...');
    
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    const venvPython = path.join(BACKEND_DIR, 'venv', 'bin', 'python');
    
    // Try venv python first, fallback to system python
    const pythonPath = fs.existsSync(venvPython) ? venvPython : pythonCmd;
    
    backendProcess = spawn(pythonPath, [BACKEND_SCRIPT], {
      cwd: BACKEND_DIR,
      stdio: 'pipe',
      env: { ...process.env, PYTHONUNBUFFERED: '1' }
    });

    backendProcess.stdout.on('data', (data) => {
      const output = data.toString();
      console.log(`Backend: ${output}`);
      // Check if backend is ready
      if (output.includes('Uvicorn running') || output.includes('Application startup complete')) {
        console.log('Backend is ready!');
      }
    });

    backendProcess.stderr.on('data', (data) => {
      const error = data.toString();
      console.error(`Backend Error: ${error}`);
    });

    backendProcess.on('close', (code) => {
      console.log(`Backend process exited with code ${code}`);
    });

    backendProcess.on('error', (error) => {
      console.error(`Failed to start backend: ${error.message}`);
    });
  });
}

function waitForBackend(callback, maxAttempts = 30) {
  const http = require('http');
  let attempts = 0;
  
  const checkBackend = () => {
    attempts++;
    const req = http.get('http://localhost:8000/health', (res) => {
      if (res.statusCode === 200) {
        console.log('Backend is ready!');
        callback();
      } else {
        if (attempts < maxAttempts) {
          setTimeout(checkBackend, 1000);
        } else {
          console.error('Backend failed to start in time');
          callback(); // Continue anyway
        }
      }
    });
    
    req.on('error', () => {
      if (attempts < maxAttempts) {
        setTimeout(checkBackend, 1000);
      } else {
        console.error('Backend failed to start');
        callback(); // Continue anyway
      }
    });
    
    req.setTimeout(1000, () => {
      req.destroy();
      if (attempts < maxAttempts) {
        setTimeout(checkBackend, 1000);
      } else {
        console.error('Backend connection timeout');
        callback(); // Continue anyway
      }
    });
  };
  
  // Start checking after a short delay
  setTimeout(checkBackend, 2000);
}

function waitForFrontend(callback, maxAttempts = 30) {
  const http = require('http');
  let attempts = 0;
  
  const checkFrontend = () => {
    attempts++;
    const req = http.get('http://localhost:9002', (res) => {
      if (res.statusCode === 200 || res.statusCode === 304) {
        console.log('Frontend is ready!');
        callback();
      } else {
        if (attempts < maxAttempts) {
          setTimeout(checkFrontend, 1000);
        } else {
          console.error('Frontend failed to start in time');
          callback(); // Continue anyway
        }
      }
    });
    
    req.on('error', () => {
      if (attempts < maxAttempts) {
        setTimeout(checkFrontend, 1000);
      } else {
        console.error('Frontend failed to start');
        callback(); // Continue anyway
      }
    });
    
    req.setTimeout(1000, () => {
      req.destroy();
      if (attempts < maxAttempts) {
        setTimeout(checkFrontend, 1000);
      } else {
        console.error('Frontend connection timeout');
        callback(); // Continue anyway
      }
    });
  };
  
  // Start checking after a short delay
  setTimeout(checkFrontend, 2000);
}

function startFrontend() {
  console.log('Starting frontend server...');
  
  // In development, we run 'npm run dev' inside the frontend directory
  frontendProcess = spawn('npm', ['run', 'dev'], {
    cwd: FRONTEND_DIR,
    shell: true,
    stdio: 'pipe'
  });

  frontendProcess.stdout.on('data', (data) => {
    console.log(`Frontend: ${data}`);
  });

  frontendProcess.stderr.on('data', (data) => {
    console.error(`Frontend Error: ${data}`);
  });

  frontendProcess.on('close', (code) => {
    console.log(`Frontend process exited with code ${code}`);
  });
}

function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Quit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload', label: 'Reload' },
        { role: 'forceReload', label: 'Force Reload' },
        { role: 'toggleDevTools', label: 'Toggle Developer Tools' },
        { type: 'separator' },
        { role: 'resetZoom', label: 'Actual Size' },
        { role: 'zoomIn', label: 'Zoom In' },
        { role: 'zoomOut', label: 'Zoom Out' },
        { type: 'separator' },
        { role: 'togglefullscreen', label: 'Toggle Fullscreen' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About H.A.R.C.',
          click: () => {
            // Show about dialog
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// Prevent default browser behavior
app.setAsDefaultProtocolClient('harc');

// Prevent opening in browser
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (event, navigationUrl) => {
    event.preventDefault();
  });
});

// App event handlers
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  // Cleanup processes
  if (backendProcess) {
    backendProcess.kill();
  }
  if (frontendProcess) {
    frontendProcess.kill();
  }

  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  // Ensure processes are killed
  if (backendProcess) {
    backendProcess.kill();
  }
  if (frontendProcess) {
    frontendProcess.kill();
  }
});
