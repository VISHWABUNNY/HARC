"use client";

import { useState, useRef, useEffect, useCallback } from 'react';
import { Camera, Grid, Thermometer, Move, ZoomIn, ZoomOut, Crosshair, Loader2, Eye, Radar, Waves } from 'lucide-react';
import { DashboardCard } from '@/components/shared/dashboard-card';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { trackHumansFromCamera, trackHumansFromLiDAR, trackHumansFromThermal, TrackingResponse } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import type { SystemMode } from "@/app/page";
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';

type ViewMode = 'normal' | 'grid' | 'thermal';
type TrackerMode = 'camera' | 'lidar' | 'thermal';

type TrackedHuman = {
  id: string;
  boundingBox: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  confidence: number;
  distance?: number;
  temperature?: number;
  speed?: number;
  direction?: number;
};

export function LiveFeedCard({ systemMode }: { systemMode: SystemMode }) {
  const { toast } = useToast();
  const [viewMode, setViewMode] = useState<ViewMode>('normal');
  const [trackerMode, setTrackerMode] = useState<TrackerMode>('camera');
  const [zoomLevel, setZoomLevel] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [humans, setHumans] = useState<TrackedHuman[]>([]);
  const [hasCameraPermission, setHasCameraPermission] = useState(false);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const getCameraPermission = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        setHasCameraPermission(true);
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (error) {
        console.error('Error accessing camera:', error);
        setHasCameraPermission(false);
        toast({
          variant: 'destructive',
          title: 'Camera Access Denied',
          description: 'Please enable camera permissions in your browser settings to use this app.',
        });
      }
    };
    getCameraPermission();
  }, [toast]);

  const captureFrame = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return null;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    if (context) {
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      return canvas.toDataURL('image/jpeg');
    }
    return null;
  }, []);

  const normalizeHumans = (result: TrackingResponse): TrackedHuman[] => {
    return result.humans.map(h => ({
      id: h.id,
      boundingBox: h.boundingBox,
      confidence: h.confidence,
      distance: h.distance,
      temperature: h.temperature,
      speed: h.movement?.speed,
      direction: h.movement?.direction,
    }));
  };

  const handleAnalyzeFeed = useCallback(async () => {
    const dataUri = captureFrame();
    if (!dataUri && trackerMode !== 'lidar') {
      toast({
        variant: "destructive",
        title: "Camera Error",
        description: "Could not capture frame from video feed.",
      });
      return;
    }

    setIsLoading(true);
    try {
      let result: TrackingResponse;

      if (trackerMode === 'camera' && dataUri) {
        result = await trackHumansFromCamera(dataUri, systemMode);
      } else if (trackerMode === 'lidar') {
        // For LiDAR, we'll use a mock data URI or actual LiDAR data
        // In a real implementation, this would come from a LiDAR sensor
        const mockLiDARData = JSON.stringify({
          points: [],
          timestamp: Date.now(),
        });
        result = await trackHumansFromLiDAR(
          `data:application/json;base64,${btoa(mockLiDARData)}`,
          dataUri
        );
      } else if (trackerMode === 'thermal' && dataUri) {
        result = await trackHumansFromThermal(dataUri, dataUri);
      } else {
        throw new Error("Invalid tracker mode or missing data");
      }

      const normalizedHumans = normalizeHumans(result);
      setHumans(normalizedHumans);
      if (normalizedHumans.length > 0) {
        setViewMode('normal');
      }
    } catch (error) {
      console.error("Error tracking humans:", error);
      toast({
        variant: "destructive",
        title: "Tracking Error",
        description: `Failed to track humans using ${trackerMode} tracker.`,
      });
    } finally {
      setIsLoading(false);
    }
  }, [captureFrame, toast, trackerMode]);

  useEffect(() => {
    let intervalId: NodeJS.Timeout;
    // Auto-analyze in Full Auto mode, and also in Manual + Aim-Bot mode for aim-bot assistance
    if ((systemMode === 'Full Auto' || systemMode === 'Manual + Aim-Bot') && hasCameraPermission) {
      handleAnalyzeFeed();
      intervalId = setInterval(handleAnalyzeFeed, 5000);
    }
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [systemMode, hasCameraPermission, handleAnalyzeFeed]);

  const getTrackerIcon = () => {
    switch (trackerMode) {
      case 'camera': return <Eye className="h-4 w-4" />;
      case 'lidar': return <Radar className="h-4 w-4" />;
      case 'thermal': return <Waves className="h-4 w-4" />;
    }
  };

  const getTrackerLabel = () => {
    switch (trackerMode) {
      case 'camera': return 'Camera Tracker';
      case 'lidar': return 'LiDAR Tracker';
      case 'thermal': return 'Thermal Tracker';
    }
  };

  return (
    <DashboardCard title="Live Feed" icon={<Camera />}>
      <div className="flex flex-col h-full">
        <div className="relative w-full aspect-video mb-4 border-2 border-primary/30 rounded-md overflow-hidden bg-black">
          <video
            ref={videoRef}
            className="w-full h-full object-cover"
            autoPlay
            muted
            playsInline
            style={{ transform: `scale(${zoomLevel})` }}
          />
          <canvas ref={canvasRef} className="hidden" />

          {humans.length > 0 && humans.map((human, index) => (
            <div key={human.id || index} className="absolute border-2 border-accent group" style={{
              left: `${(human.boundingBox.x / (videoRef.current?.videoWidth || 1)) * 100}%`,
              top: `${(human.boundingBox.y / (videoRef.current?.videoHeight || 1)) * 100}%`,
              width: `${(human.boundingBox.width / (videoRef.current?.videoWidth || 1)) * 100}%`,
              height: `${(human.boundingBox.height / (videoRef.current?.videoHeight || 1)) * 100}%`,
            }}>
              <span className="absolute -top-6 left-0 text-xs font-mono bg-accent text-black px-1 rounded-sm z-10">
                {trackerMode === 'thermal' && human.temperature ? `${human.temperature.toFixed(1)}°C` : `CONF: ${human.confidence.toFixed(0)}%`}
              </span>
              {human.distance && (
                <span className="absolute -top-6 right-0 text-xs font-mono bg-primary text-primary-foreground px-1 rounded-sm z-10">
                  {human.distance.toFixed(1)}m
                </span>
              )}
              {human.speed !== undefined && (
                <span className="absolute -bottom-6 left-0 text-xs font-mono bg-accent/80 text-black px-1 rounded-sm z-10">
                  {human.speed.toFixed(1)} m/s
                </span>
              )}
              <div className="absolute bottom-1 right-1 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button variant="destructive" size="icon" className="h-6 w-6"><Crosshair/></Button>
              </div>
            </div>
          ))}

          {viewMode === 'grid' && humans.length === 0 && (
            <div className="absolute inset-0 grid grid-cols-3 grid-rows-3">
              {[...Array(9)].map((_, i) => (
                <div key={i} className="border border-accent/30" />
              ))}
            </div>
          )}
          {!hasCameraPermission && trackerMode !== 'lidar' && (
            <div className="absolute inset-0 flex items-center justify-center p-4">
              <Alert variant="destructive">
                <AlertTitle>Camera Access Required</AlertTitle>
                <AlertDescription>
                  Please allow camera access in your browser to use the live feed feature.
                </AlertDescription>
              </Alert>
            </div>
          )}
        </div>
        
        <div className="flex flex-col gap-2 mb-2">
          <div className="flex items-center gap-2">
            <span className="text-xs sm:text-sm text-muted-foreground font-mono">Tracker:</span>
            <Select value={trackerMode} onValueChange={(value: TrackerMode) => { setTrackerMode(value); setHumans([]); }}>
              <SelectTrigger className="h-8 w-full sm:w-[180px] text-xs sm:text-sm">
                <div className="flex items-center gap-2">
                  {getTrackerIcon()}
                  <SelectValue />
                </div>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="camera">
                  Live Camera
                </SelectItem>
                <SelectItem value="lidar">
                  LiDAR
                </SelectItem>
                <SelectItem value="thermal">
                  Thermal
                </SelectItem>
              </SelectContent>
            </Select>
            {humans.length > 0 && (
              <span className="text-xs sm:text-sm font-mono text-accent ml-auto">
                {humans.length} {humans.length === 1 ? 'Human' : 'Humans'} Detected
              </span>
            )}
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2">
          <div className="flex gap-1 justify-center sm:justify-start">
            <Button variant={viewMode === 'normal' && humans.length === 0 ? "destructive" : "outline"} size="icon" className="h-7 w-7 sm:h-8 sm:w-8" onClick={() => { setHumans([]); setViewMode('normal'); }}><Move className="h-4 w-4"/></Button>
            <Button variant={viewMode === 'grid' ? "destructive" : "outline"} size="icon" className="h-7 w-7 sm:h-8 sm:w-8" onClick={() => { setHumans([]); setViewMode('grid'); }}><Grid className="h-4 w-4"/></Button>
            <Button variant={viewMode === 'thermal' ? "destructive" : "outline"} size="icon" className="h-7 w-7 sm:h-8 sm:w-8" onClick={() => { setHumans([]); setViewMode('thermal'); }} disabled={trackerMode !== 'thermal'}><Thermometer className="h-4 w-4"/></Button>
          </div>
          <Separator orientation="vertical" className="hidden sm:block h-6 bg-primary/30" />
          <Separator orientation="horizontal" className="sm:hidden h-px bg-primary/30" />
          <div className="flex items-center gap-2 justify-center sm:justify-end">
            <span className="font-mono text-xs sm:text-sm text-muted-foreground">ZOOM</span>
            <Button variant="outline" size="icon" className="h-7 w-7 sm:h-8 sm:w-8" onClick={() => setZoomLevel(z => Math.max(1, z - 0.2))}><ZoomOut className="h-4 w-4"/></Button>
            <Button variant="outline" size="icon" className="h-7 w-7 sm:h-8 sm:w-8" onClick={() => setZoomLevel(z => Math.min(3, z + 0.2))}><ZoomIn className="h-4 w-4"/></Button>
          </div>
        </div>
        <div className="mt-3 sm:mt-4 flex-grow flex items-center justify-center">
          <Button onClick={handleAnalyzeFeed} disabled={isLoading || (systemMode !== 'Manual' && systemMode !== 'Manual + Aim-Bot') || (!hasCameraPermission && trackerMode !== 'lidar')} variant="destructive" className="w-full text-xs sm:text-sm">
            {isLoading ? <Loader2 className="mr-2 h-3 w-3 sm:h-4 sm:w-4 animate-spin" /> : getTrackerIcon()}
            <span className="ml-2 hidden sm:inline">Track Humans ({getTrackerLabel()})</span>
            <span className="ml-2 sm:hidden">Track</span>
          </Button>
        </div>
      </div>
    </DashboardCard>
  );
}
