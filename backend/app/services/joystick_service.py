"""
Joystick Input Service

Reads input from Linux joystick device (/dev/input/js0)
and converts it to cannon control commands.
"""

import struct
import os
from typing import Optional, Dict, Tuple
from app.services.hardware_config import get_hardware_config

class JoystickService:
    """Handles joystick input reading."""
    
    # Linux joystick event structure
    # struct js_event {
    #     __u32 time;     /* event timestamp in milliseconds */
    #     __s16 value;    /* value */
    #     __u8 type;      /* event type */
    #     __u8 number;    /* axis/button number */
    # }
    JS_EVENT_BUTTON = 0x01
    JS_EVENT_AXIS = 0x02
    JS_EVENT_INIT = 0x80
    
    def __init__(self):
        self.hw_config = get_hardware_config()
        self.joystick_fd: Optional[int] = None
        self.is_connected = False
        self.axis_values: Dict[int, float] = {}  # axis_number -> value (-1.0 to 1.0)
        self.button_states: Dict[int, bool] = {}  # button_number -> pressed
        
    def connect(self) -> bool:
        """Connect to joystick device."""
        if not self.hw_config.is_enabled("joystick"):
            return False
        
        joystick_path = self.hw_config.get_path("joystick")
        if not joystick_path or not os.path.exists(joystick_path):
            print(f"⚠️  Joystick device not found: {joystick_path}")
            return False
        
        try:
            self.joystick_fd = os.open(joystick_path, os.O_RDONLY | os.O_NONBLOCK)
            self.is_connected = True
            print(f"✅ Joystick connected: {joystick_path}")
            return True
        except Exception as e:
            print(f"❌ Error connecting to joystick: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Disconnect from joystick."""
        if self.joystick_fd:
            try:
                os.close(self.joystick_fd)
            except:
                pass
            self.joystick_fd = None
        self.is_connected = False
    
    def read_event(self) -> Optional[Dict]:
        """
        Read a single joystick event.
        
        Returns:
            Dict with keys: type, number, value, time
            or None if no event available
        """
        if not self.is_connected or not self.joystick_fd:
            return None
        
        try:
            # Read 8 bytes (js_event structure)
            data = os.read(self.joystick_fd, 8)
            if len(data) != 8:
                return None
            
            # Unpack: unsigned int (time), short (value), unsigned char (type), unsigned char (number)
            time_ms, value, event_type, number = struct.unpack('IhBB', data)
            
            # Normalize axis values to -1.0 to 1.0 range
            normalized_value = value / 32767.0 if event_type == self.JS_EVENT_AXIS else value
            
            event = {
                'type': event_type,
                'number': number,
                'value': normalized_value,
                'raw_value': value,
                'time': time_ms
            }
            
            # Update internal state
            if event_type == self.JS_EVENT_AXIS:
                self.axis_values[number] = normalized_value
            elif event_type == self.JS_EVENT_BUTTON:
                self.button_states[number] = bool(value)
            
            return event
        except BlockingIOError:
            # No data available (non-blocking read)
            return None
        except Exception as e:
            print(f"Error reading joystick: {e}")
            return None
    
    def get_axis(self, axis_number: int) -> float:
        """Get current value of an axis (-1.0 to 1.0)."""
        return self.axis_values.get(axis_number, 0.0)
    
    def get_button(self, button_number: int) -> bool:
        """Get current state of a button."""
        return self.button_states.get(button_number, False)
    
    def get_cannon_control(self) -> Dict[str, float]:
        """
        Get cannon control values from joystick.
        
        Returns:
            Dict with 'x', 'y' (cannon position delta) and 'spray' (boolean)
        """
        # Typical joystick mapping:
        # Axis 0: X (left/right)
        # Axis 1: Y (up/down)
        # Button 0: Spray/Trigger
        
        x_delta = self.get_axis(0)  # Left stick X
        y_delta = -self.get_axis(1)  # Left stick Y (inverted)
        spray = self.get_button(0)  # Trigger button
        
        return {
            'x': x_delta,
            'y': y_delta,
            'spray': spray
        }
    
    def __del__(self):
        """Cleanup on destruction."""
        self.disconnect()

# Global instance
_joystick_service: Optional[JoystickService] = None

def get_joystick_service() -> JoystickService:
    """Get global joystick service instance."""
    global _joystick_service
    if _joystick_service is None:
        _joystick_service = JoystickService()
        _joystick_service.connect()
    return _joystick_service

