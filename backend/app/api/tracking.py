from fastapi import APIRouter, HTTPException, Query
from app.models.tracking import TrackingRequest, TrackingResponse, LiDARTrackingRequest, ThermalTrackingRequest
from app.services.ai_service import AIService
from app.services.auto_targeting_service import get_auto_targeting_service

router = APIRouter()
ai_service = AIService()
auto_targeting = get_auto_targeting_service()

@router.post("/camera", response_model=TrackingResponse)
async def track_humans_camera(
    request: TrackingRequest,
    ai_mode: str = Query("Manual", description="AI mode: Manual, Manual + Aim-Bot, or Full Auto")
):
    """Track humans from live camera feed."""
    try:
        humans = await ai_service.track_humans_from_camera(request.cameraFeedDataUri)
        
        # Update joystick bridge with detected humans for aim-bot assistance
        from app.services.joystick_motor_bridge import get_joystick_motor_bridge
        try:
            bridge = get_joystick_motor_bridge()
            if bridge:
                bridge.update_detected_humans(humans)
        except:
            pass  # Bridge might not be initialized
        
        # If Full Auto mode, process automated targeting
        if ai_mode == "Full Auto" and auto_targeting.is_active:
            # Process detection for automated targeting
            targeting_result = await auto_targeting.process_detection(humans)
            # targeting_result contains status and actions taken
        
        return TrackingResponse(humans=humans)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking humans: {str(e)}")

@router.post("/lidar", response_model=TrackingResponse)
async def track_humans_lidar(request: LiDARTrackingRequest):
    """Track humans from LiDAR point cloud data."""
    try:
        humans = await ai_service.track_humans_from_lidar(
            request.lidarDataUri,
            request.cameraFeedDataUri
        )
        return TrackingResponse(humans=humans)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking humans with LiDAR: {str(e)}")

@router.post("/thermal", response_model=TrackingResponse)
async def track_humans_thermal(request: ThermalTrackingRequest):
    """Track humans from thermal imaging feed."""
    try:
        humans = await ai_service.track_humans_from_thermal(
            request.thermalFeedDataUri,
            request.cameraFeedDataUri
        )
        return TrackingResponse(humans=humans)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking humans with thermal: {str(e)}")

