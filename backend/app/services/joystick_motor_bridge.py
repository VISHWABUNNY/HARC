"""
Joystick to Motor Controller Bridge

Continuously reads joystick input and sends commands to motor controller.
This runs in a background thread to keep joystick and motor in sync.
Supports aim-bot assistance mode for enhanced targeting.
"""

import threading
import time
from typing import Optional
from app.services.joystick_service import get_joystick_service
from app.services.motor_controller_service import get_motor_controller_service
from app.services.aimbot_assistance_service import get_aimbot_assistance_service

class JoystickMotorBridge:
    """Bridges joystick input to motor controller output."""
    
    def __init__(self):
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.update_interval = 0.05  # 50ms = 20Hz update rate
        self.current_mode = "Manual"  # Track current system mode
        self.last_detected_humans = []  # Store last detection for aim-bot
        
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
    
    def set_mode(self, mode: str):
        """Set current system mode (affects aim-bot assistance)."""
        self.current_mode = mode
        aimbot = get_aimbot_assistance_service()
        if mode == "Manual + Aim-Bot":
            aimbot.start()
        else:
            aimbot.stop()
    
    def update_detected_humans(self, humans: list):
        """Update detected humans for aim-bot assistance."""
        self.last_detected_humans = humans
    
    def _run(self):
        """Main loop: read joystick, send to motor controller."""
        joystick = get_joystick_service()
        motor = get_motor_controller_service()
        aimbot = get_aimbot_assistance_service()
        
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
                    
                    # Get current cannon position for aim-bot assistance
                    from app.services.system_service import system_service
                    current_pos = system_service.cannon_position
                    
                    # Apply aim-bot assistance if in Manual + Aim-Bot mode
                    if self.current_mode == "Manual + Aim-Bot" and aimbot.is_active:
                        assisted_x, assisted_y = aimbot.assist_joystick_input(
                            control['x'],
                            control['y'],
                            self.last_detected_humans,
                            current_pos
                        )
                        # Use assisted values
                        final_x = assisted_x
                        final_y = assisted_y
                    else:
                        # Pure joystick input
                        final_x = control['x']
                        final_y = control['y']
                    
                    # Send movement commands if input moved
                    if abs(final_x) > 0.1 or abs(final_y) > 0.1:  # Dead zone
                        motor.move_cannon(final_x, final_y)
                
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

def get_joystick_motor_bridge() -> Optional[JoystickMotorBridge]:
    """Get the joystick-motor bridge instance."""
    global _bridge
    return _bridge

