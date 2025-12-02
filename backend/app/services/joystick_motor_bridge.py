"""
Joystick to Motor Controller Bridge

Continuously reads joystick input and sends commands to motor controller.
This runs in a background thread to keep joystick and motor in sync.
"""

import threading
import time
from typing import Optional
from app.services.joystick_service import get_joystick_service
from app.services.motor_controller_service import get_motor_controller_service

class JoystickMotorBridge:
    """Bridges joystick input to motor controller output."""
    
    def __init__(self):
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.update_interval = 0.05  # 50ms = 20Hz update rate
        
    def start(self):
        """Start the bridge thread."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print("✅ Joystick-Motor bridge started")
    
    def stop(self):
        """Stop the bridge thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        print("⏹️  Joystick-Motor bridge stopped")
    
    def _run(self):
        """Main loop: read joystick, send to motor controller."""
        joystick = get_joystick_service()
        motor = get_motor_controller_service()
        
        while self.running:
            try:
                # Only process if both are connected
                if joystick.is_connected and motor.is_connected:
                    # Read joystick events
                    while True:
                        event = joystick.read_event()
                        if event is None:
                            break
                        
                        # Process button events (spray)
                        if event['type'] == joystick.JS_EVENT_BUTTON and event['number'] == 0:
                            if event['raw_value']:
                                motor.start_spray()
                            else:
                                motor.stop_spray()
                    
                    # Get current joystick control values
                    control = joystick.get_cannon_control()
                    
                    # Send movement commands if joystick moved
                    if abs(control['x']) > 0.1 or abs(control['y']) > 0.1:  # Dead zone
                        motor.move_cannon(control['x'], control['y'])
                
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"Error in joystick-motor bridge: {e}")
                time.sleep(0.1)
    
    def __del__(self):
        """Cleanup on destruction."""
        self.stop()

# Global instance
_bridge: Optional[JoystickMotorBridge] = None

def start_joystick_motor_bridge():
    """Start the joystick-motor bridge."""
    global _bridge
    if _bridge is None:
        _bridge = JoystickMotorBridge()
    _bridge.start()

def stop_joystick_motor_bridge():
    """Stop the joystick-motor bridge."""
    global _bridge
    if _bridge:
        _bridge.stop()

