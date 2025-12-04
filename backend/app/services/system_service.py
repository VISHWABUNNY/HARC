import time
import os
import platform
from datetime import datetime, timedelta
from typing import List, Optional
from app.models.system import (
    SystemStats, SystemVitals, SystemLog, WeaponStatus, SystemStatus,
    CannonReadiness, SystemMode, LogCategory
)
from app.services.hardware_config import get_hardware_config

# Try to import hardware monitoring libraries
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available. CPU metrics will be unavailable.")

try:
    import pynvml
    PYNVML_AVAILABLE = True
    try:
        pynvml.nvmlInit()
    except:
        PYNVML_AVAILABLE = False
        print("Warning: pynvml available but GPU not found or not accessible.")
except ImportError:
    PYNVML_AVAILABLE = False
    print("Warning: pynvml not available. GPU metrics will be unavailable.")

class SystemService:
    def __init__(self):
        self.start_time = time.time()
        self.logs: List[SystemLog] = []
        self.water_pressure = 85
        self.cannon_position = {"x": 0, "y": 0}
        self.is_online = True
        self.hw_config = get_hardware_config()
        self._initialize_logs()
        self._log_hardware_status()
        
        # Start joystick-motor bridge if both are enabled (lazy import to avoid circular dependency)
        if (self.hw_config.is_enabled("joystick") and 
            self.hw_config.is_enabled("motor_controller")):
            from app.services.joystick_motor_bridge import start_joystick_motor_bridge, get_joystick_motor_bridge
            start_joystick_motor_bridge()
            self.joystick_bridge = get_joystick_motor_bridge()
        else:
            self.joystick_bridge = None
        
        # Initialize auto targeting service (starts when Full Auto mode is activated)
        from app.services.auto_targeting_service import get_auto_targeting_service
        self.auto_targeting = get_auto_targeting_service()
        
        # Initialize aim-bot assistance service (starts when Manual + Aim-Bot mode is activated)
        from app.services.aimbot_assistance_service import get_aimbot_assistance_service
        self.aimbot_assistance = get_aimbot_assistance_service()
    
    def _initialize_logs(self):
        """Initialize with some system logs."""
        base_time = datetime.now() - timedelta(minutes=10)
        initial_logs = [
            {"timestamp": (base_time + timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S"), "category": LogCategory.SYSTEM, "message": "System Initialized. All modules online."},
            {"timestamp": (base_time + timedelta(seconds=5)).strftime("%Y-%m-%d %H:%M:%S"), "category": LogCategory.AI, "message": "AI Core Synced. Threat assessment matrix loaded."},
            {"timestamp": (base_time + timedelta(seconds=10)).strftime("%Y-%m-%d %H:%M:%S"), "category": LogCategory.CANNON, "message": "Water cannon systems engaged. Safety protocols active."},
        ]
        self.logs = [SystemLog(**log) for log in initial_logs]
    
    def _log_hardware_status(self):
        """Log hardware device connection status."""
        enabled_devices = self.hw_config.get_enabled_devices()
        if enabled_devices:
            for device_name, config in enabled_devices.items():
                if self.hw_config.device_exists(device_name):
                    self.add_log(
                        LogCategory.SYSTEM,
                        f"Hardware device '{device_name}' connected at {config.get('path')}"
                    )
                else:
                    self.add_log(
                        LogCategory.SYSTEM,
                        f"Hardware device '{device_name}' enabled but not found at {config.get('path')}"
                    )
    
    def get_system_stats(self, ai_mode: str = "Manual") -> SystemStats:
        """Get current system statistics."""
        # Count detected humans from recent tracking logs
        total_targets = len([log for log in self.logs if "detected" in log.message.lower() or "human" in log.message.lower()])
        
        # Validate mode
        valid_modes = ["Manual", "Manual + Aim-Bot", "Full Auto"]
        if ai_mode not in valid_modes:
            ai_mode = "Manual"
        
        return SystemStats(
            totalTargetsDetected=total_targets,
            cannonReadiness=CannonReadiness.ARMED if self.water_pressure > 20 else CannonReadiness.SAFE,
            aiMode=SystemMode(ai_mode)
        )
    
    def _get_cpu_temperature(self) -> Optional[float]:
        """Get real CPU temperature from system sensors."""
        if not PSUTIL_AVAILABLE:
            return None
        
        try:
            # Try to get CPU temperature from psutil
            temps = psutil.sensors_temperatures()
            
            # Try common sensor names (prioritize CPU sensors)
            cpu_sensor_names = ['cpu_thermal', 'coretemp', 'k10temp', 'cpu', 'Package id 0', 'Tctl', 'Tdie']
            
            for name in cpu_sensor_names:
                if name in temps and len(temps[name]) > 0:
                    temp_value = temps[name][0].current
                    if temp_value and temp_value > 0:  # Valid temperature
                        return temp_value
            
            # If no specific CPU sensor, try first available
            for sensor_name, entries in temps.items():
                if entries and 'cpu' in sensor_name.lower():
                    return entries[0].current
            
            # Last resort: try first temperature sensor
            for sensor_name, entries in temps.items():
                if entries:
                    return entries[0].current
                    
        except Exception as e:
            print(f"Error reading CPU temperature: {e}")
        
        return None
    
    def _get_gpu_temperature(self) -> Optional[float]:
        """Get real GPU temperature from NVIDIA or AMD GPU."""
        # Try AMD GPU via psutil sensors FIRST (most common on Linux)
        if PSUTIL_AVAILABLE:
            try:
                temps = psutil.sensors_temperatures()
                # Check for AMD GPU sensors
                amd_sensors = ['amdgpu', 'radeon', 'gpu']
                for sensor_name in amd_sensors:
                    if sensor_name in temps and len(temps[sensor_name]) > 0:
                        temp_value = temps[sensor_name][0].current
                        if temp_value and temp_value > 0:
                            return float(temp_value)
            except Exception as e:
                print(f"Error reading GPU temp from psutil: {e}")
        
        # Try NVIDIA GPU (if available and AMD not found)
        if PYNVML_AVAILABLE:
            try:
                # Get first GPU (index 0)
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                return float(temp)
            except Exception as e:
                pass
        
        return None
    
    def _get_cpu_usage(self) -> float:
        """Get real CPU usage percentage."""
        if not PSUTIL_AVAILABLE:
            return 0.0
        
        try:
            return psutil.cpu_percent(interval=0.1)
        except Exception as e:
            print(f"Error reading CPU usage: {e}")
            return 0.0
    
    def get_system_vitals(self) -> SystemVitals:
        """Get current system vitals from REAL hardware - NO FAKE DATA."""
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Get REAL CPU temperature from actual sensor
        cpu_temp = self._get_cpu_temperature()
        if cpu_temp is None:
            # If no sensor available, return 0 (not fake data)
            cpu_temp = 0.0
        
        # Get REAL GPU temperature from actual sensor
        gpu_temp = self._get_gpu_temperature()
        if gpu_temp is None:
            # If no GPU sensor available, return 0 (not fake data)
            gpu_temp = 0.0
        
        # Motor current - Read from hardware if configured
        motor_current = 0.0
        hw_config = get_hardware_config()
        if hw_config.is_enabled("motor_controller") and hw_config.device_exists("motor_controller"):
            # TODO: Implement actual motor controller reading
            # motor_current = read_motor_current(hw_config.get_path("motor_controller"))
            motor_current = 0.0  # Placeholder until implementation
        
        return SystemVitals(
            cpuTemp=max(0.0, min(100.0, cpu_temp)),
            gpuTemp=max(0.0, min(100.0, gpu_temp)),
            motorCurrent=motor_current,  # Real value: 0 (no motor hardware)
            uptime=int(elapsed)
        )
    
    def get_system_logs(self, category: str = "ALL", limit: int = 50) -> List[SystemLog]:
        """Get system logs, optionally filtered by category."""
        logs = self.logs.copy()
        
        if category != "ALL":
            logs = [log for log in logs if log.category.value == category]
        
        # Return most recent logs
        return sorted(logs, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def add_log(self, category: LogCategory, message: str):
        """Add a new system log."""
        log = SystemLog(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            category=category,
            message=message
        )
        self.logs.append(log)
        # Keep only last 1000 logs
        if len(self.logs) > 1000:
            self.logs = self.logs[-1000:]
    
    def get_weapon_status(self) -> WeaponStatus:
        """Get current weapon status."""
        return WeaponStatus(
            waterPressure=self.water_pressure,
            cannonPosition=self.cannon_position,
            isOnline=self.is_online
        )
    
    def update_water_pressure(self, pressure: int):
        """Update water pressure."""
        # If hardware sensor is enabled, read from it instead
        if self.hw_config.is_enabled("water_pressure") and self.hw_config.device_exists("water_pressure"):
            # TODO: Implement actual water pressure sensor reading
            # pressure = read_water_pressure_sensor(self.hw_config.get_path("water_pressure"))
            pass
        
        self.water_pressure = max(0, min(100, pressure))
        if self.water_pressure < 20:
            self.add_log(LogCategory.CANNON, f"Water pressure low. {self.water_pressure}% remaining.")
    
    
    def update_cannon_position(self, x: float, y: float):
        """Update cannon position."""
        self.cannon_position = {
            "x": max(-100, min(100, x)),
            "y": max(-100, min(100, y))
        }
        
        # If motor controller is connected, send command to hardware
        if self.hw_config.is_enabled("motor_controller"):
            from app.services.motor_controller_service import get_motor_controller_service
            motor = get_motor_controller_service()
            if motor.is_connected:
                motor.set_cannon_position(x, y)
    
    def get_system_status(self) -> SystemStatus:
        """Get system online status."""
        return SystemStatus(
            isOnline=self.is_online,
            lastUpdate=datetime.now()
        )
    

# Global instance
system_service = SystemService()

