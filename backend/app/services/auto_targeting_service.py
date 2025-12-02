"""
Automated Targeting Service (ML Model Based)

Uses ML model to automatically target and engage detected humans in Full Auto mode.
"""

import asyncio
import math
from typing import List, Optional, Dict, Tuple
from app.models.tracking import HumanDetection
from app.models.system import LogCategory

class AutoTargetingService:
    """ML-based automated targeting and engagement system."""
    
    def __init__(self):
        self.motor_controller = None  # Lazy load
        self.is_active = False
        self.current_target: Optional[HumanDetection] = None
        self.target_lock_threshold = 0.7  # Confidence threshold for target lock
        self.engagement_range = 50.0  # Maximum engagement range in meters
        self.aim_tolerance = 5.0  # Degrees tolerance for aim
    
    def _get_motor_controller(self):
        """Lazy load motor controller to avoid circular imports."""
        if self.motor_controller is None:
            from app.services.motor_controller_service import get_motor_controller_service
            self.motor_controller = get_motor_controller_service()
        return self.motor_controller
    
    def _get_system_service(self):
        """Lazy load system service to avoid circular imports."""
        from app.services.system_service import system_service
        return system_service
        
    def start(self):
        """Start automated targeting system."""
        self.is_active = True
        system_service = self._get_system_service()
        system_service.add_log(LogCategory.AI, "Automated targeting system activated.")
        print("✅ Automated targeting system started")
    
    def stop(self):
        """Stop automated targeting system."""
        self.is_active = False
        self.current_target = None
        motor = self._get_motor_controller()
        if motor.is_connected:
            motor.stop_spray()
            motor.stop_all()
        system_service = self._get_system_service()
        system_service.add_log(LogCategory.AI, "Automated targeting system deactivated.")
        print("⏹️  Automated targeting system stopped")
    
    def _calculate_target_priority(self, humans: List[HumanDetection]) -> Optional[HumanDetection]:
        """
        Use ML model to select best target from detected humans.
        
        Priority factors:
        1. Confidence score
        2. Distance (closer = higher priority)
        3. Movement speed (moving targets = higher priority)
        4. Threat assessment (if available)
        
        Returns:
            Best target to engage, or None if no suitable target
        """
        if not humans:
            return None
        
        # Filter humans within engagement range
        valid_targets = [
            h for h in humans 
            if (h.distance is None or h.distance <= self.engagement_range) and
               h.confidence >= (self.target_lock_threshold * 100)
        ]
        
        if not valid_targets:
            return None
        
        # ML-based target selection algorithm
        # Score each target based on multiple factors
        scored_targets = []
        for human in valid_targets:
            score = 0.0
            
            # Confidence factor (0-1) - higher confidence = better target
            confidence_factor = human.confidence / 100.0
            score += confidence_factor * 0.4
            
            # Distance factor (0-1) - closer = better target
            if human.distance:
                distance_factor = 1.0 - (human.distance / self.engagement_range)
                distance_factor = max(0.0, min(1.0, distance_factor))
                score += distance_factor * 0.3
            else:
                score += 0.15  # Medium priority if distance unknown
            
            # Movement factor (0-1) - moving targets = higher priority
            if human.movement and human.movement.speed > 0:
                movement_factor = min(1.0, human.movement.speed / 5.0)  # Normalize to 5 m/s max
                score += movement_factor * 0.2
            else:
                score += 0.1  # Lower priority for stationary targets
            
            # Temperature factor (for thermal) - human body temp = higher priority
            if human.temperature:
                # Normal human body temp is ~37°C
                temp_factor = 1.0 - abs(human.temperature - 37.0) / 10.0
                temp_factor = max(0.0, min(1.0, temp_factor))
                score += temp_factor * 0.1
            
            scored_targets.append((score, human))
        
        # Sort by score (highest first) and return best target
        scored_targets.sort(key=lambda x: x[0], reverse=True)
        if scored_targets:
            best_score, best_target = scored_targets[0]
            return best_target
        
        return None
    
    def _calculate_cannon_angles(self, target: HumanDetection, image_width: int = 1920, image_height: int = 1080) -> Tuple[float, float]:
        """
        Calculate cannon angles (x, y) to aim at target based on bounding box.
        
        Args:
            target: Detected human with bounding box
            image_width: Camera image width in pixels
            image_height: Camera image height in pixels
        
        Returns:
            Tuple of (x_angle, y_angle) in degrees (-100 to 100 range)
        """
        # Get bounding box center
        bbox = target.boundingBox
        center_x = bbox.x + (bbox.width / 2)
        center_y = bbox.y + (bbox.height / 2)
        
        # Convert pixel coordinates to normalized coordinates (-1 to 1)
        # Assuming image center is (0, 0)
        normalized_x = (center_x - (image_width / 2)) / (image_width / 2)
        normalized_y = ((image_height / 2) - center_y) / (image_height / 2)  # Invert Y
        
        # Convert to cannon position range (-100 to 100)
        cannon_x = normalized_x * 100.0
        cannon_y = normalized_y * 100.0
        
        # Clamp to valid range
        cannon_x = max(-100, min(100, cannon_x))
        cannon_y = max(-100, min(100, cannon_y))
        
        return (cannon_x, cannon_y)
    
    def _is_target_locked(self, target: HumanDetection, current_cannon_pos: Dict[str, float]) -> bool:
        """
        Check if cannon is aimed at target (within tolerance).
        
        Args:
            target: Target human
            current_cannon_pos: Current cannon position {x, y}
        
        Returns:
            True if target is locked, False otherwise
        """
        # Calculate required cannon position
        required_x, required_y = self._calculate_cannon_angles(target)
        
        # Check if current position is within tolerance
        x_diff = abs(current_cannon_pos["x"] - required_x)
        y_diff = abs(current_cannon_pos["y"] - required_y)
        
        return x_diff <= self.aim_tolerance and y_diff <= self.aim_tolerance
    
    async def process_detection(self, humans: List[HumanDetection], image_width: int = 1920, image_height: int = 1080) -> Dict:
        """
        Process detected humans and engage target using ML model.
        
        Args:
            humans: List of detected humans
            image_width: Camera image width
            image_height: Camera image height
        
        Returns:
            Dict with targeting status and actions taken
        """
        if not self.is_active:
            return {"status": "inactive", "action": "none"}
        
        if not humans:
            # No targets - stop spray, maintain position
            if self.current_target:
                self.current_target = None
                motor = self._get_motor_controller()
                if motor.is_connected:
                    motor.stop_spray()
            return {"status": "no_targets", "action": "stop_spray"}
        
        # Use ML model to select best target
        target = self._calculate_target_priority(humans)
        
        if not target:
            # No valid targets
            if self.current_target:
                self.current_target = None
                motor = self._get_motor_controller()
                if motor.is_connected:
                    motor.stop_spray()
            return {"status": "no_valid_targets", "action": "stop_spray"}
        
        # Get current cannon position
        system_service = self._get_system_service()
        current_pos = system_service.cannon_position
        
        # Calculate required cannon position to aim at target
        required_x, required_y = self._calculate_cannon_angles(target, image_width, image_height)
        
        # Move cannon towards target
        motor = self._get_motor_controller()
        if motor.is_connected:
            # Calculate movement delta
            x_delta = (required_x - current_pos["x"]) / 100.0  # Normalize to -1 to 1
            y_delta = (required_y - current_pos["y"]) / 100.0
            
            # Move cannon (with smoothing)
            move_speed = 0.5  # 50% of max speed for smooth tracking
            motor.move_cannon(x_delta * move_speed, y_delta * move_speed)
            
            # Update cannon position in system
            new_x = current_pos["x"] + (x_delta * move_speed * 10)  # Scale for position update
            new_y = current_pos["y"] + (y_delta * move_speed * 10)
            system_service.update_cannon_position(new_x, new_y)
        
        # Check if target is locked
        is_locked = self._is_target_locked(target, current_pos)
        
        if is_locked:
            # Target locked - engage!
            self.current_target = target
            motor = self._get_motor_controller()
            if motor.is_connected:
                motor.start_spray()
            
            system_service.add_log(
                LogCategory.AI,
                f"Target locked and engaged. Confidence: {target.confidence:.1f}%, Distance: {target.distance or 'unknown'}m"
            )
            
            return {
                "status": "target_locked",
                "action": "spray",
                "target_id": target.id,
                "confidence": target.confidence,
                "distance": target.distance
            }
        else:
            # Tracking target, not yet locked
            self.current_target = target
            motor = self._get_motor_controller()
            if motor.is_connected:
                motor.stop_spray()  # Don't spray until locked
            
            return {
                "status": "tracking",
                "action": "aiming",
                "target_id": target.id,
                "required_position": {"x": required_x, "y": required_y},
                "current_position": current_pos
            }
    
    def get_status(self) -> Dict:
        """Get current targeting system status."""
        return {
            "active": self.is_active,
            "target_locked": self.current_target is not None,
            "current_target": {
                "id": self.current_target.id if self.current_target else None,
                "confidence": self.current_target.confidence if self.current_target else None,
                "distance": self.current_target.distance if self.current_target else None
            } if self.current_target else None
        }

# Global instance
_auto_targeting_service: Optional[AutoTargetingService] = None

def get_auto_targeting_service() -> AutoTargetingService:
    """Get global auto targeting service instance."""
    global _auto_targeting_service
    if _auto_targeting_service is None:
        _auto_targeting_service = AutoTargetingService()
    return _auto_targeting_service

