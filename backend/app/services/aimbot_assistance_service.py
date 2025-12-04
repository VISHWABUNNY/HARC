"""
Aim-Bot Assistance Service

Provides aim-bot assistance for manual joystick control.
Blends joystick input with auto-targeting suggestions to help user aim.
"""

import math
from typing import Optional, Dict, Tuple, List
from app.models.tracking import HumanDetection
from app.models.system import LogCategory

class AimBotAssistanceService:
    """Aim-bot assistance that helps guide joystick input to targets."""
    
    def __init__(self):
        self.is_active = False
        self.assistance_strength = 0.5  # 0.0 = no assistance, 1.0 = full assistance
        self.current_target: Optional[HumanDetection] = None
        self.target_lock_threshold = 0.6  # Confidence threshold for assistance
        self.assistance_range = 10.0  # Degrees - how close to target before assistance kicks in
    
    def _get_system_service(self):
        """Lazy load system service to avoid circular imports."""
        from app.services.system_service import system_service
        return system_service
    
    def _get_auto_targeting_service(self):
        """Lazy load auto targeting service."""
        from app.services.auto_targeting_service import get_auto_targeting_service
        return get_auto_targeting_service()
    
    def start(self):
        """Start aim-bot assistance."""
        self.is_active = True
        system_service = self._get_system_service()
        system_service.add_log(LogCategory.AI, "Aim-bot assistance activated. Manual control with targeting help enabled.")
        print("✅ Aim-bot assistance started")
    
    def stop(self):
        """Stop aim-bot assistance."""
        self.is_active = False
        self.current_target = None
        system_service = self._get_system_service()
        system_service.add_log(LogCategory.AI, "Aim-bot assistance deactivated.")
        print("⏹️  Aim-bot assistance stopped")
    
    def set_assistance_strength(self, strength: float):
        """Set assistance strength (0.0 to 1.0)."""
        self.assistance_strength = max(0.0, min(1.0, strength))
    
    def _calculate_target_priority(self, humans: List[HumanDetection]) -> Optional[HumanDetection]:
        """
        Select best target for assistance (closest, highest confidence).
        
        Returns:
            Best target to assist with, or None if no suitable target
        """
        if not humans:
            return None
        
        # Filter humans with sufficient confidence
        valid_targets = [
            h for h in humans 
            if h.confidence >= (self.target_lock_threshold * 100)
        ]
        
        if not valid_targets:
            return None
        
        # Select target based on:
        # 1. Confidence (higher = better)
        # 2. Distance (closer = better, if available)
        # 3. Center of frame (closer to center = better)
        
        scored_targets = []
        for human in valid_targets:
            score = 0.0
            
            # Confidence factor (0-1)
            confidence_factor = human.confidence / 100.0
            score += confidence_factor * 0.5
            
            # Distance factor (0-1) - closer is better
            if human.distance:
                distance_factor = 1.0 / (1.0 + human.distance / 50.0)  # Normalize
                score += distance_factor * 0.3
            else:
                score += 0.15
            
            # Center position factor (0-1) - closer to center is better
            bbox = human.boundingBox
            center_x = bbox.x + (bbox.width / 2)
            center_y = bbox.y + (bbox.height / 2)
            # Assuming 1920x1080 image
            center_distance = math.sqrt(
                (center_x - 960) ** 2 + (center_y - 540) ** 2
            )
            center_factor = 1.0 / (1.0 + center_distance / 500.0)
            score += center_factor * 0.2
            
            scored_targets.append((score, human))
        
        # Sort by score and return best
        scored_targets.sort(key=lambda x: x[0], reverse=True)
        if scored_targets:
            return scored_targets[0][1]
        
        return None
    
    def _calculate_target_angles(self, target: HumanDetection, image_width: int = 1920, image_height: int = 1080) -> Tuple[float, float]:
        """
        Calculate cannon angles to aim at target.
        
        Returns:
            Tuple of (x_angle, y_angle) in degrees (-100 to 100 range)
        """
        bbox = target.boundingBox
        center_x = bbox.x + (bbox.width / 2)
        center_y = bbox.y + (bbox.height / 2)
        
        # Convert pixel coordinates to normalized coordinates (-1 to 1)
        normalized_x = (center_x - (image_width / 2)) / (image_width / 2)
        normalized_y = ((image_height / 2) - center_y) / (image_height / 2)  # Invert Y
        
        # Convert to cannon position range (-100 to 100)
        cannon_x = normalized_x * 100.0
        cannon_y = normalized_y * 100.0
        
        # Clamp to valid range
        cannon_x = max(-100, min(100, cannon_x))
        cannon_y = max(-100, min(100, cannon_y))
        
        return (cannon_x, cannon_y)
    
    def assist_joystick_input(
        self, 
        joystick_x: float, 
        joystick_y: float,
        humans: List[HumanDetection],
        current_cannon_pos: Dict[str, float],
        image_width: int = 1920,
        image_height: int = 1080
    ) -> Tuple[float, float]:
        """
        Blend joystick input with aim-bot assistance.
        
        Args:
            joystick_x: Joystick X input (-1.0 to 1.0)
            joystick_y: Joystick Y input (-1.0 to 1.0)
            humans: List of detected humans
            current_cannon_pos: Current cannon position {x, y}
            image_width: Camera image width
            image_height: Camera image height
        
        Returns:
            Tuple of (assisted_x, assisted_y) - blended joystick + aim-bot input
        """
        if not self.is_active:
            # No assistance - return joystick input as-is
            return (joystick_x, joystick_y)
        
        if not humans:
            # No targets - return joystick input as-is
            self.current_target = None
            return (joystick_x, joystick_y)
        
        # Find best target for assistance
        target = self._calculate_target_priority(humans)
        
        if not target:
            # No valid target - return joystick input as-is
            self.current_target = None
            return (joystick_x, joystick_y)
        
        self.current_target = target
        
        # Calculate target position
        target_x, target_y = self._calculate_target_angles(target, image_width, image_height)
        
        # Calculate direction from current position to target
        delta_x = target_x - current_cannon_pos["x"]
        delta_y = target_y - current_cannon_pos["y"]
        
        # Normalize to -1.0 to 1.0 range (for joystick-like input)
        max_delta = max(abs(delta_x), abs(delta_y), 1.0)  # Avoid division by zero
        target_direction_x = delta_x / max_delta
        target_direction_y = delta_y / max_delta
        
        # Calculate distance to target (in cannon position units)
        distance_to_target = math.sqrt(delta_x ** 2 + delta_y ** 2)
        
        # Determine assistance strength based on distance
        # Closer to target = stronger assistance
        if distance_to_target < self.assistance_range:
            # Very close - strong assistance
            local_strength = self.assistance_strength * 1.0
        elif distance_to_target < self.assistance_range * 2:
            # Medium distance - moderate assistance
            local_strength = self.assistance_strength * 0.7
        else:
            # Far away - light assistance
            local_strength = self.assistance_strength * 0.3
        
        # Blend joystick input with aim-bot direction
        # Formula: (1 - strength) * joystick + strength * aim_bot
        assisted_x = (1.0 - local_strength) * joystick_x + local_strength * target_direction_x
        assisted_y = (1.0 - local_strength) * joystick_y + local_strength * target_direction_y
        
        # Clamp to valid range
        assisted_x = max(-1.0, min(1.0, assisted_x))
        assisted_y = max(-1.0, min(1.0, assisted_y))
        
        return (assisted_x, assisted_y)
    
    def get_status(self) -> Dict:
        """Get current aim-bot assistance status."""
        return {
            "active": self.is_active,
            "assistance_strength": self.assistance_strength,
            "target_locked": self.current_target is not None,
            "current_target": {
                "id": self.current_target.id if self.current_target else None,
                "confidence": self.current_target.confidence if self.current_target else None,
                "distance": self.current_target.distance if self.current_target else None
            } if self.current_target else None
        }

# Global instance
_aimbot_assistance_service: Optional[AimBotAssistanceService] = None

def get_aimbot_assistance_service() -> AimBotAssistanceService:
    """Get global aim-bot assistance service instance."""
    global _aimbot_assistance_service
    if _aimbot_assistance_service is None:
        _aimbot_assistance_service = AimBotAssistanceService()
    return _aimbot_assistance_service

