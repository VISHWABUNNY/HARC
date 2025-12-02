from pydantic import BaseModel
from typing import Optional, List

class BoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float

class Coordinates(BaseModel):
    latitude: float
    longitude: float

class Movement(BaseModel):
    speed: float
    direction: float

class HumanDetection(BaseModel):
    id: str
    boundingBox: BoundingBox
    coordinates: Coordinates
    confidence: float
    distance: Optional[float] = None
    temperature: Optional[float] = None
    movement: Optional[Movement] = None

class TrackingRequest(BaseModel):
    cameraFeedDataUri: str

class TrackingResponse(BaseModel):
    humans: List[HumanDetection]

class LiDARTrackingRequest(BaseModel):
    lidarDataUri: str
    cameraFeedDataUri: Optional[str] = None

class ThermalTrackingRequest(BaseModel):
    thermalFeedDataUri: str
    cameraFeedDataUri: Optional[str] = None

