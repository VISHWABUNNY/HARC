const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const REQUEST_TIMEOUT = 5000; // 5 seconds timeout

// Helper function to add timeout to fetch requests
async function fetchWithTimeout(url: string, options: RequestInit = {}, timeout: number = REQUEST_TIMEOUT): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error: any) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new Error(`Request timeout: Backend not responding (${timeout}ms). Is the backend running on ${API_BASE_URL}?`);
    }
    if (error.message?.includes('Failed to fetch') || error.message?.includes('NetworkError')) {
      throw new Error(`Cannot connect to backend at ${API_BASE_URL}. Is the server running?`);
    }
    throw error;
  }
}

export interface HumanDetection {
  id: string;
  boundingBox: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  coordinates: {
    latitude: number;
    longitude: number;
  };
  confidence: number;
  distance?: number;
  temperature?: number;
  movement?: {
    speed: number;
    direction: number;
  };
}

export interface TrackingResponse {
  humans: HumanDetection[];
}

export interface SystemStats {
  totalTargetsDetected: number;
  cannonReadiness: "ARMED" | "SAFE" | "MAINTENANCE";
  aiMode: "Manual" | "Manual + Aim-Bot" | "Full Auto";
}

export interface SystemVitals {
  cpuTemp: number;
  gpuTemp: number;
  motorCurrent: number;
  uptime: number;
}

export interface SystemLog {
  timestamp: string;
  category: "SYSTEM" | "CANNON" | "AI";
  message: string;
}

export interface WeaponStatus {
  waterPressure: number;
  cannonPosition: { x: number; y: number };
  isOnline: boolean;
}

export interface SystemStatus {
  isOnline: boolean;
  lastUpdate: string;
}

// Tracking APIs
export async function trackHumansFromCamera(cameraFeedDataUri: string, aiMode: string = "Manual"): Promise<TrackingResponse> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/tracking/camera?aiMode=${encodeURIComponent(aiMode)}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ cameraFeedDataUri }),
  });

  if (!response.ok) {
    throw new Error(`Tracking failed: ${response.statusText}`);
  }

  return response.json();
}

export async function trackHumansFromLiDAR(
  lidarDataUri: string,
  cameraFeedDataUri?: string
): Promise<TrackingResponse> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/tracking/lidar`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ lidarDataUri, cameraFeedDataUri }),
  });

  if (!response.ok) {
    throw new Error(`LiDAR tracking failed: ${response.statusText}`);
  }

  return response.json();
}

export async function trackHumansFromThermal(
  thermalFeedDataUri: string,
  cameraFeedDataUri?: string
): Promise<TrackingResponse> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/tracking/thermal`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ thermalFeedDataUri, cameraFeedDataUri }),
  });

  if (!response.ok) {
    throw new Error(`Thermal tracking failed: ${response.statusText}`);
  }

  return response.json();
}

// System APIs
export async function getSystemStats(aiMode: string = "Manual"): Promise<SystemStats> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/system/stats?aiMode=${encodeURIComponent(aiMode)}`);
  if (!response.ok) {
    throw new Error(`Failed to get system stats: ${response.statusText}`);
  }
  return response.json();
}

export async function getSystemVitals(): Promise<SystemVitals> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/system/vitals`);
  if (!response.ok) {
    throw new Error(`Failed to get system vitals: ${response.statusText}`);
  }
  return response.json();
}

export async function getSystemLogs(category: string = "ALL", limit: number = 50): Promise<SystemLog[]> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/system/logs?category=${category}&limit=${limit}`);
  if (!response.ok) {
    throw new Error(`Failed to get system logs: ${response.statusText}`);
  }
  return response.json();
}

export async function getWeaponStatus(): Promise<WeaponStatus> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/system/weapon`);
  if (!response.ok) {
    throw new Error(`Failed to get weapon status: ${response.statusText}`);
  }
  return response.json();
}

export async function updateWaterPressure(pressure: number): Promise<void> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/system/weapon/pressure`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ pressure }),
  });
  if (!response.ok) {
    throw new Error(`Failed to update water pressure: ${response.statusText}`);
  }
}

export async function updateCannonPosition(x: number, y: number): Promise<void> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/system/weapon/position`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ x, y }),
  });
  if (!response.ok) {
    throw new Error(`Failed to update cannon position: ${response.statusText}`);
  }
}

export async function getSystemStatus(): Promise<SystemStatus> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/system/status`);
  if (!response.ok) {
    throw new Error(`Failed to get system status: ${response.statusText}`);
  }
  return response.json();
}

// Auto Targeting APIs
export async function startAutoTargeting(): Promise<void> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/system/auto-targeting/start`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Failed to start auto targeting: ${response.statusText}`);
  }
}

export async function stopAutoTargeting(): Promise<void> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/system/auto-targeting/stop`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Failed to stop auto targeting: ${response.statusText}`);
  }
}

export async function getAutoTargetingStatus(): Promise<any> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/system/auto-targeting/status`);
  if (!response.ok) {
    throw new Error(`Failed to get auto targeting status: ${response.statusText}`);
  }
  return response.json();
}

// Aim-Bot Assistance APIs
export async function startAimbotAssistance(): Promise<void> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/system/aimbot-assistance/start`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Failed to start aim-bot assistance: ${response.statusText}`);
  }
}

export async function stopAimbotAssistance(): Promise<void> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/system/aimbot-assistance/stop`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Failed to stop aim-bot assistance: ${response.statusText}`);
  }
}

export async function getAimbotAssistanceStatus(): Promise<any> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/system/aimbot-assistance/status`);
  if (!response.ok) {
    throw new Error(`Failed to get aim-bot assistance status: ${response.statusText}`);
  }
  return response.json();
}
