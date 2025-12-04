"use client";

import { useState, useEffect, useCallback } from 'react';
import { Zap, ChevronUp, ChevronDown, ChevronLeft, ChevronRight } from 'lucide-react';
import { DashboardCard } from '@/components/shared/dashboard-card';
import { Progress } from '@/components/ui/progress';
import { Label } from '@/components/ui/label';
import type { SystemMode } from "@/app/page";
import { useInterval } from '@/hooks/use-interval';
import { cn } from '@/lib/utils';
import { getWeaponStatus, updateWaterPressure, updateCannonPosition, WeaponStatus } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

const Joystick = ({ onMove, onSpray, disabled }: { onMove: (dx: number, dy: number) => void; onSpray: () => void; disabled?: boolean }) => {
    const [activeDirection, setActiveDirection] = useState<string | null>(null);

    const handleMove = (dx: number, dy: number, direction: string) => {
        if (disabled) return;
        setActiveDirection(direction);
        onMove(dx, dy);
    };

    useInterval(() => {
        if (activeDirection && !disabled) {
            switch (activeDirection) {
                case 'up': onMove(0, -1); break;
                case 'down': onMove(0, 1); break;
                case 'left': onMove(-1, 0); break;
                case 'right': onMove(1, 0); break;
            }
        }
    }, 100);

    const baseButtonClass = "absolute bg-primary/20 hover:bg-primary/50 text-primary-foreground rounded-none transition-colors";
    const activeClass = "bg-accent text-accent-foreground";
    
    return (
        <div className="relative w-40 h-40 sm:w-48 sm:h-48 mx-auto" onMouseUp={() => setActiveDirection(null)} onMouseLeave={() => setActiveDirection(null)}>
            {/* Directional Buttons */}
            <button
                onMouseDown={() => handleMove(0, -1, 'up')}
                className={cn(baseButtonClass, "top-0 left-1/2 -translate-x-1/2 h-12 w-16 rounded-t-md", { [activeClass]: activeDirection === 'up' })}
                disabled={disabled}
            >
                <ChevronUp className="w-8 h-8 mx-auto" />
            </button>
            <button
                onMouseDown={() => handleMove(0, 1, 'down')}
                className={cn(baseButtonClass, "bottom-0 left-1/2 -translate-x-1/2 h-12 w-16 rounded-b-md", { [activeClass]: activeDirection === 'down' })}
                disabled={disabled}
            >
                <ChevronDown className="w-8 h-8 mx-auto" />
            </button>
            <button
                onMouseDown={() => handleMove(-1, 0, 'left')}
                className={cn(baseButtonClass, "top-1/2 left-0 -translate-y-1/2 h-16 w-12 rounded-l-md", { [activeClass]: activeDirection === 'left' })}
                disabled={disabled}
            >
                <ChevronLeft className="w-8 h-8 mx-auto" />
            </button>
            <button
                onMouseDown={() => handleMove(1, 0, 'right')}
                className={cn(baseButtonClass, "top-1/2 right-0 -translate-y-1/2 h-16 w-12 rounded-r-md", { [activeClass]: activeDirection === 'right' })}
                disabled={disabled}
            >
                <ChevronRight className="w-8 h-8 mx-auto" />
            </button>

            {/* Spray Button */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-16 h-16 sm:w-20 sm:h-20">
                <button
                    onClick={onSpray}
                    disabled={disabled}
                    className="w-full h-full rounded-full bg-destructive/50 border-2 sm:border-4 border-destructive/80 text-destructive-foreground font-headline text-sm sm:text-lg tracking-widest transition-colors hover:bg-destructive active:bg-red-700 disabled:bg-muted disabled:border-muted-foreground disabled:cursor-not-allowed"
                >
                    SPRAY
                </button>
            </div>
        </div>
    );
};


export function WeaponControlCard({ systemMode }: { systemMode: SystemMode }) {
  const { toast } = useToast();
  const [weaponStatus, setWeaponStatus] = useState<WeaponStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchWeaponStatus = async () => {
      try {
        const status = await getWeaponStatus();
        setWeaponStatus(status);
      } catch (error) {
        console.error("Error fetching weapon status:", error);
        toast({
          variant: "destructive",
          title: "Error",
          description: "Failed to load weapon status.",
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchWeaponStatus();
    const interval = setInterval(fetchWeaponStatus, 1000); // Update every second
    return () => clearInterval(interval);
  }, [toast]);

  const handleCannonMove = useCallback(async (dx: number, dy: number) => {
    if (!weaponStatus) return;
    
    const newX = Math.max(-100, Math.min(100, weaponStatus.cannonPosition.x + dx * 2));
    const newY = Math.max(-100, Math.min(100, weaponStatus.cannonPosition.y + dy * 2));
    
    try {
      await updateCannonPosition(newX, newY);
      setWeaponStatus(prev => prev ? { ...prev, cannonPosition: { x: newX, y: newY } } : null);
    } catch (error) {
      console.error("Error updating cannon position:", error);
    }
  }, [weaponStatus]);

  const handleSpray = useCallback(async () => {
    if (!weaponStatus) return;
    
    const newPressure = Math.max(0, weaponStatus.waterPressure - 5);
    
    try {
      await updateWaterPressure(newPressure);
      setWeaponStatus(prev => prev ? { ...prev, waterPressure: newPressure } : null);
    } catch (error) {
      console.error("Error updating water pressure:", error);
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to update water pressure.",
      });
    }
  }, [weaponStatus, toast]);

  const isManual = systemMode === 'Manual' || systemMode === 'Manual + Aim-Bot';
  const isFullAuto = systemMode === 'Full Auto';
  const isAimbotMode = systemMode === 'Manual + Aim-Bot';
  
  const getStatusText = () => {
    if (isFullAuto) return "AI CONTROL ACTIVE";
    if (isAimbotMode) return "MANUAL + AIM-BOT";
    return "MANUAL CONTROL";
  }

  if (isLoading || !weaponStatus) {
    return (
      <DashboardCard title="Water Cannon Control" icon={<Zap />}>
        <div className="flex flex-col items-center justify-center h-full">
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </DashboardCard>
    );
  }

  return (
    <DashboardCard title="Water Cannon Control" icon={<Zap />}>
      <div className="flex flex-col items-center justify-around h-full">
        {isManual ? (
            <Joystick onMove={handleCannonMove} onSpray={handleSpray} disabled={false}/>
        ) : (
            <div className="w-40 h-40 sm:w-48 sm:h-48 mx-auto flex flex-col items-center justify-center bg-black/30 rounded-full border-2 border-dashed border-primary/50">
                <p className="font-headline text-sm sm:text-lg text-accent animate-pulse text-center leading-tight px-2">
                    {getStatusText()}
                </p>
            </div>
        )}

        <div className="w-full space-y-3 sm:space-y-4 px-2 sm:px-4 mt-3 sm:mt-4">
            <div className="space-y-1">
                <Label className="text-xs sm:text-sm text-muted-foreground">WATER PRESSURE: {weaponStatus.waterPressure}%</Label>
                <Progress value={weaponStatus.waterPressure} className="h-2 [&>div]:bg-accent" />
            </div>
             <div className="flex gap-2">
                <div className="w-full border border-input rounded-md p-2 text-center bg-black/20">
                    <Label className="text-xs text-muted-foreground">CANNON POSITION</Label>
                    <p className="font-mono text-accent text-xs sm:text-sm">X: {weaponStatus.cannonPosition.x.toFixed(0)} | Y: {weaponStatus.cannonPosition.y.toFixed(0)}</p>
                </div>
            </div>
        </div>
      </div>
    </DashboardCard>
  );
}
