"""
Motor Controller Output Service

Sends commands to motor controller via serial port (/dev/ttyUSB1)
to control water cannon movement and spray.
"""

import serial
import time
import os
from typing import Optional, Dict
from app.services.hardware_config import get_hardware_config

class MotorControllerService:
    """Handles motor controller communication."""
    
    def __init__(self):
        self.hw_config = get_hardware_config()
        self.serial_connection: Optional[serial.Serial] = None
        self.is_connected = False
        self.current_position = {"x": 0.0, "y": 0.0}
        self.water_spray_active = False
        
    def connect(self) -> bool:
        """Connect to motor controller via serial port."""
        if not self.hw_config.is_enabled("motor_controller"):
            return False
        
        device_path = self.hw_config.get_path("motor_controller")
        if not device_path or not os.path.exists(device_path):
            print(f"⚠️  Motor controller device not found: {device_path}")
            return False
        
        try:
            # Get baudrate from config
            baudrate = self.hw_config.get_device_config("motor_controller").get("baudrate", 9600)
            
            self.serial_connection = serial.Serial(
                port=device_path,
                baudrate=baudrate,
                timeout=1,
                write_timeout=1
            )
            self.is_connected = True
            print(f"✅ Motor controller connected: {device_path} @ {baudrate} baud")
            
            # Initialize motor controller (send reset/home command)
            self._send_command("RESET")
            time.sleep(0.5)
            
            return True
        except serial.SerialException as e:
            print(f"❌ Serial error connecting to motor controller: {e}")
            self.is_connected = False
            return False
        except Exception as e:
            print(f"❌ Error connecting to motor controller: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Disconnect from motor controller."""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                # Stop all motors before disconnecting
                self._send_command("STOP")
                self.serial_connection.close()
            except:
                pass
            self.serial_connection = None
        self.is_connected = False
    
    def _send_command(self, command: str) -> bool:
        """
        Send a command to the motor controller.
        
        Args:
            command: Command string to send
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.is_connected or not self.serial_connection:
            return False
        
        try:
            # Format: "COMMAND\n"
            cmd_bytes = f"{command}\n".encode('ascii')
            self.serial_connection.write(cmd_bytes)
            self.serial_connection.flush()
            return True
        except Exception as e:
            print(f"Error sending command to motor controller: {e}")
            return False
    
    def move_cannon(self, x_delta: float, y_delta: float) -> bool:
        """
        Move cannon by delta values.
        
        Args:
            x_delta: X movement (-1.0 to 1.0, negative = left, positive = right)
            y_delta: Y movement (-1.0 to 1.0, negative = down, positive = up)
        
        Returns:
            True if command sent successfully
        """
        if not self.is_connected:
            return False
        
        # Convert normalized values to motor steps/speed
        # Adjust these multipliers based on your motor controller
        x_speed = int(x_delta * 100)  # -100 to 100
        y_speed = int(y_delta * 100)  # -100 to 100
        
        # Update internal position
        self.current_position["x"] += x_delta * 0.1  # Scale for position tracking
        self.current_position["y"] += y_delta * 0.1
        
        # Send movement command
        # Format: "MOVE X Y" where X and Y are speeds
        command = f"MOVE {x_speed} {y_speed}"
        return self._send_command(command)
    
    def set_cannon_position(self, x: float, y: float) -> bool:
        """
        Set cannon to absolute position.
        
        Args:
            x: X position (-100 to 100)
            y: Y position (-100 to 100)
        
        Returns:
            True if command sent successfully
        """
        if not self.is_connected:
            return False
        
        # Clamp values
        x = max(-100, min(100, x))
        y = max(-100, min(100, y))
        
        self.current_position["x"] = x
        self.current_position["y"] = y
        
        # Send position command
        # Format: "POS X Y" where X and Y are absolute positions
        command = f"POS {int(x)} {int(y)}"
        return self._send_command(command)
    
    def start_spray(self) -> bool:
        """Start water spray."""
        if not self.is_connected:
            return False
        
        self.water_spray_active = True
        return self._send_command("SPRAY ON")
    
    def stop_spray(self) -> bool:
        """Stop water spray."""
        if not self.is_connected:
            return False
        
        self.water_spray_active = False
        return self._send_command("SPRAY OFF")
    
    def set_spray(self, active: bool) -> bool:
        """Set spray state."""
        if active:
            return self.start_spray()
        else:
            return self.stop_spray()
    
    def stop_all(self) -> bool:
        """Stop all motors immediately."""
        if not self.is_connected:
            return False
        
        return self._send_command("STOP")
    
    def get_status(self) -> Dict:
        """Get current motor controller status."""
        return {
            "connected": self.is_connected,
            "position": self.current_position.copy(),
            "spray_active": self.water_spray_active
        }
    
    def __del__(self):
        """Cleanup on destruction."""
        self.disconnect()

# Global instance
_motor_controller_service: Optional[MotorControllerService] = None

def get_motor_controller_service() -> MotorControllerService:
    """Get global motor controller service instance."""
    global _motor_controller_service
    if _motor_controller_service is None:
        _motor_controller_service = MotorControllerService()
        _motor_controller_service.connect()
    return _motor_controller_service

