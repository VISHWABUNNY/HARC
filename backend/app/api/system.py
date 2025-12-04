from fastapi import APIRouter, HTTPException
from typing import Optional
from app.models.system import SystemStats, SystemVitals, SystemLog, WeaponStatus, SystemStatus
from app.services.system_service import system_service
from app.models.system import LogCategory
from app.services.auto_targeting_service import get_auto_targeting_service

router = APIRouter()
auto_targeting = get_auto_targeting_service()

@router.get("/stats", response_model=SystemStats)
async def get_system_stats(aiMode: Optional[str] = "Manual"):
    """Get current system statistics."""
    try:
        return system_service.get_system_stats(aiMode or "Manual")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system stats: {str(e)}")

@router.get("/vitals", response_model=SystemVitals)
async def get_system_vitals():
    """Get current system vitals (CPU, GPU, motor, uptime)."""
    try:
        return system_service.get_system_vitals()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system vitals: {str(e)}")

@router.get("/logs", response_model=list[SystemLog])
async def get_system_logs(category: Optional[str] = "ALL", limit: int = 50):
    """Get system logs, optionally filtered by category."""
    try:
        return system_service.get_system_logs(category, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system logs: {str(e)}")

@router.post("/logs")
async def add_system_log(category: str, message: str):
    """Add a new system log."""
    try:
        log_category = LogCategory(category)
        system_service.add_log(log_category, message)
        return {"status": "success", "message": "Log added"}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding log: {str(e)}")

@router.get("/weapon", response_model=WeaponStatus)
async def get_weapon_status():
    """Get current weapon status (water pressure, cannon position)."""
    try:
        return system_service.get_weapon_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting weapon status: {str(e)}")

@router.put("/weapon/pressure")
async def update_water_pressure(pressure: int):
    """Update water pressure (0-100)."""
    try:
        system_service.update_water_pressure(pressure)
        system_service.add_log(
            LogCategory.CANNON,
            f"Water pressure updated to {pressure}%"
        )
        return {"status": "success", "pressure": system_service.water_pressure}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating water pressure: {str(e)}")

@router.put("/weapon/position")
async def update_cannon_position(x: float, y: float):
    """Update cannon position."""
    try:
        system_service.update_cannon_position(x, y)
        return {"status": "success", "position": system_service.cannon_position}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating cannon position: {str(e)}")

@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    """Get system online status."""
    try:
        return system_service.get_system_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system status: {str(e)}")

@router.post("/auto-targeting/start")
async def start_auto_targeting():
    """Start automated targeting system (Full Auto mode)."""
    try:
        auto_targeting.start()
        # Update joystick bridge mode
        from app.services.joystick_motor_bridge import get_joystick_motor_bridge
        bridge = get_joystick_motor_bridge()
        if bridge:
            bridge.set_mode("Full Auto")
        return {"status": "success", "message": "Automated targeting system started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting auto targeting: {str(e)}")

@router.post("/auto-targeting/stop")
async def stop_auto_targeting():
    """Stop automated targeting system."""
    try:
        auto_targeting.stop()
        # Update joystick bridge mode
        from app.services.joystick_motor_bridge import get_joystick_motor_bridge
        bridge = get_joystick_motor_bridge()
        if bridge:
            bridge.set_mode("Manual")
        return {"status": "success", "message": "Automated targeting system stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping auto targeting: {str(e)}")

@router.get("/auto-targeting/status")
async def get_auto_targeting_status():
    """Get automated targeting system status."""
    try:
        return auto_targeting.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting auto targeting status: {str(e)}")

@router.post("/aimbot-assistance/start")
async def start_aimbot_assistance():
    """Start aim-bot assistance (Manual + Aim-Bot mode)."""
    try:
        from app.services.aimbot_assistance_service import get_aimbot_assistance_service
        aimbot = get_aimbot_assistance_service()
        aimbot.start()
        # Update joystick bridge mode
        from app.services.joystick_motor_bridge import get_joystick_motor_bridge
        bridge = get_joystick_motor_bridge()
        if bridge:
            bridge.set_mode("Manual + Aim-Bot")
        return {"status": "success", "message": "Aim-bot assistance started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting aim-bot assistance: {str(e)}")

@router.post("/aimbot-assistance/stop")
async def stop_aimbot_assistance():
    """Stop aim-bot assistance."""
    try:
        from app.services.aimbot_assistance_service import get_aimbot_assistance_service
        aimbot = get_aimbot_assistance_service()
        aimbot.stop()
        # Update joystick bridge mode
        from app.services.joystick_motor_bridge import get_joystick_motor_bridge
        bridge = get_joystick_motor_bridge()
        if bridge:
            bridge.set_mode("Manual")
        return {"status": "success", "message": "Aim-bot assistance stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping aim-bot assistance: {str(e)}")

@router.get("/aimbot-assistance/status")
async def get_aimbot_assistance_status():
    """Get aim-bot assistance status."""
    try:
        from app.services.aimbot_assistance_service import get_aimbot_assistance_service
        aimbot = get_aimbot_assistance_service()
        return aimbot.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting aim-bot assistance status: {str(e)}")
