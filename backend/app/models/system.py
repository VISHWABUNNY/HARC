from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class CannonReadiness(str, Enum):
    ARMED = "ARMED"
    SAFE = "SAFE"
    MAINTENANCE = "MAINTENANCE"

class SystemMode(str, Enum):
    MANUAL = "Manual"
    MANUAL_AIMBOT = "Manual + Aim-Bot"
    FULL_AUTO = "Full Auto"

class LogCategory(str, Enum):
    SYSTEM = "SYSTEM"
    CANNON = "CANNON"
    AI = "AI"

class SystemStats(BaseModel):
    totalTargetsDetected: int
    cannonReadiness: CannonReadiness
    aiMode: SystemMode

class SystemVitals(BaseModel):
    cpuTemp: float
    gpuTemp: float
    motorCurrent: float
    uptime: int  # seconds since start

class SystemLog(BaseModel):
    timestamp: str
    category: LogCategory
    message: str

class WeaponStatus(BaseModel):
    waterPressure: int  # 0-100
    cannonPosition: dict  # {x: float, y: float}
    isOnline: bool

class SystemStatus(BaseModel):
    isOnline: bool
    lastUpdate: datetime

