const { spawn, execSync, spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

const isWin = os.platform() === 'win32';
const rootDir = process.cwd();
const backendDir = path.join(rootDir, 'backend');
const frontendDir = path.join(rootDir, 'frontend');

function runCommand(cmd, args, options = {}) {
  console.log(`\n🚀 Running: ${cmd} ${args.join(' ')}`);
  return new Promise((resolve, reject) => {
    const proc = spawn(cmd, args, {
      stdio: 'inherit',
      shell: true,
      ...options
    });

    proc.on('close', (code) => {
      if (code === 0) resolve();
      else reject(new Error(`Command ${cmd} failed with code ${code}`));
    });
  });
}

async function install() {
  console.log('📦 Installing Dependencies...');

  // 1. Backend
  console.log('\n🐍 Setting up Backend...');
  const venvDir = path.join(backendDir, 'venv');
  if (!fs.existsSync(venvDir)) {
    const pythonCmd = isWin ? 'python' : 'python3';
    try {
      execSync(`${pythonCmd} -m venv venv`, { cwd: backendDir, stdio: 'inherit' });
    } catch (e) {
      console.error(`❌ Failed to create virtual environment. Ensure ${pythonCmd} is installed.`);
      process.exit(1);
    }
  }

  const pipCmd = isWin 
    ? path.join(venvDir, 'Scripts', 'pip.exe')
    : path.join(venvDir, 'bin', 'pip');
  
  await runCommand(pipCmd, ['install', '--upgrade', 'pip'], { cwd: backendDir });
  await runCommand(pipCmd, ['install', '-r', 'requirements.txt'], { cwd: backendDir });

  // 2. Frontend
  console.log('\n⚛️ Installing Frontend...');
  await runCommand('npm', ['install'], { cwd: frontendDir });

  console.log('\n✅ Installation Complete!');
}

async function start() {
  console.log('🎯 Starting H.A.R.C. System...');
  
  // Ensure node_modules exists
  if (!fs.existsSync(path.join(frontendDir, 'node_modules'))) {
    await install();
  }

  // Build frontend if needed
  if (!fs.existsSync(path.join(frontendDir, '.next'))) {
    console.log('🔨 Building frontend...');
    await runCommand('npm', ['run', 'build'], { cwd: frontendDir });
  }

  // Run Electron
  await runCommand('npm', ['run', 'electron:start'], { cwd: frontendDir });
}

async function build() {
  console.log('🔨 Building Distribution...');
  if (!fs.existsSync(path.join(frontendDir, 'node_modules'))) {
    await install();
  }
  
  await runCommand('npm', ['run', 'build'], { cwd: frontendDir });
  
  const target = isWin ? '--win' : '--linux';
  await runCommand('npx', ['electron-builder', target], { cwd: frontendDir });
}

async function cleanup() {
  console.log('🧹 Cleaning up unwanted root files...');
  const filesToRemove = [
    'AIMBOT_FEATURE.md',
    'install-run.bat'
  ];

  filesToRemove.forEach(file => {
    const filePath = path.join(rootDir, file);
    if (fs.existsSync(filePath)) {
      try {
        fs.unlinkSync(filePath);
        console.log(`  ✅ Removed ${file}`);
      } catch (e) {
        console.error(`  ❌ Failed to remove ${file}: ${e.message}`);
      }
    }
  });
}

const action = process.argv[2] || 'start';

(async () => {
  try {
    switch (action) {
      case 'cleanup':
        await cleanup();
        break;
      case 'install':
        await install();
        break;
      case 'start':
        await start();
        break;
      case 'build':
        await build();
        break;
      default:
        console.log(`Unknown action: ${action}. Use: install, start, build`);
    }
  } catch (e) {
    console.error(`\n❌ Error: ${e.message}`);
    process.exit(1);
  }
})();
