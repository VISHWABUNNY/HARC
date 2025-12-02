"""
Hardware Configuration Manager

This module loads and manages hardware device configurations from hardware_config.json.
Update the paths in hardware_config.json to match your actual hardware connections.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Any

class HardwareConfig:
    """Manages hardware device configurations."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize hardware configuration.
        
        Args:
            config_path: Path to hardware_config.json file. 
                        Defaults to backend/hardware_config.json
        """
        if config_path is None:
            # Get the backend directory (parent of app/)
            # __file__ is: backend/app/services/hardware_config.py
            # backend_dir should be: backend/
            backend_dir = Path(__file__).parent.parent.parent
            config_path = backend_dir / "hardware_config.json"
        
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from JSON file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                print(f"✅ Loaded hardware config from {self.config_path}")
            else:
                print(f"⚠️  Hardware config file not found: {self.config_path}")
                print("   Using default configuration (all devices disabled)")
                self.config = self._get_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing hardware config: {e}")
            print("   Using default configuration")
            self.config = self._get_default_config()
        except Exception as e:
            print(f"❌ Error loading hardware config: {e}")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "camera": {"enabled": False, "path": "/dev/video0", "type": "v4l2"},
            "lidar": {"enabled": False, "path": "/dev/ttyUSB0", "type": "serial", "baudrate": 115200},
            "thermal": {"enabled": False, "path": "/dev/i2c-1", "type": "i2c", "address": "0x5A"},
            "water_pressure": {"enabled": False, "path": "/dev/ttyACM0", "type": "serial", "baudrate": 9600},
            "joystick": {"enabled": False, "path": "/dev/input/js0", "type": "linux_joystick"},
            "motor_controller": {"enabled": False, "path": "/dev/ttyUSB1", "type": "serial", "baudrate": 9600}
        }
    
    def get_device_config(self, device_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific device.
        
        Args:
            device_name: Name of the device (camera, lidar, thermal, etc.)
        
        Returns:
            Device configuration dict or None if not found
        """
        return self.config.get(device_name)
    
    def is_enabled(self, device_name: str) -> bool:
        """Check if a device is enabled."""
        device_config = self.get_device_config(device_name)
        if device_config:
            return device_config.get("enabled", False)
        return False
    
    def get_path(self, device_name: str) -> Optional[str]:
        """Get device path."""
        device_config = self.get_device_config(device_name)
        if device_config:
            return device_config.get("path")
        return None
    
    def get_type(self, device_name: str) -> Optional[str]:
        """Get device type."""
        device_config = self.get_device_config(device_name)
        if device_config:
            return device_config.get("type")
        return None
    
    def device_exists(self, device_name: str) -> bool:
        """Check if device path exists on the system."""
        path = self.get_path(device_name)
        if path:
            return os.path.exists(path)
        return False
    
    def get_all_devices(self) -> Dict[str, Dict[str, Any]]:
        """Get all device configurations."""
        return self.config.copy()
    
    def get_enabled_devices(self) -> Dict[str, Dict[str, Any]]:
        """Get only enabled devices."""
        return {
            name: config 
            for name, config in self.config.items() 
            if config.get("enabled", False)
        }
    
    def reload_config(self) -> None:
        """Reload configuration from file."""
        self.load_config()

# Global instance
_hardware_config: Optional[HardwareConfig] = None

def get_hardware_config() -> HardwareConfig:
    """Get global hardware configuration instance."""
    global _hardware_config
    if _hardware_config is None:
        _hardware_config = HardwareConfig()
    return _hardware_config

