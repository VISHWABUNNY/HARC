"use client";

import { useState, useEffect } from 'react';
import { Settings } from 'lucide-react';
import { DashboardCard } from '@/components/shared/dashboard-card';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { startAutoTargeting, stopAutoTargeting, startAimbotAssistance, stopAimbotAssistance } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import type { SystemMode } from "@/app/page";

type ModeSelectorCardProps = {
  systemMode: SystemMode;
  setSystemMode: (mode: SystemMode) => void;
};

export function ModeSelectorCard({ systemMode, setSystemMode }: ModeSelectorCardProps) {
  const { toast } = useToast();
  const [isSwitching, setIsSwitching] = useState(false);

  const handleModeChange = async (value: SystemMode) => {
    setIsSwitching(true);
    try {
      if (value === "Full Auto") {
        // Start ML-based auto targeting
        await stopAimbotAssistance(); // Stop aim-bot if active
        await startAutoTargeting();
        toast({
          title: "Full Auto Mode Activated",
          description: "ML model is now controlling the system automatically.",
        });
      } else if (value === "Manual + Aim-Bot") {
        // Start aim-bot assistance
        await stopAutoTargeting(); // Stop full auto if active
        await startAimbotAssistance();
        toast({
          title: "Manual + Aim-Bot Mode Activated",
          description: "Manual control with aim-bot assistance enabled.",
        });
      } else {
        // Manual mode - stop all assistance
        await stopAutoTargeting();
        await stopAimbotAssistance();
        toast({
          title: "Manual Mode Activated",
          description: "Manual control enabled.",
        });
      }
      setSystemMode(value);
    } catch (error) {
      console.error("Error switching mode:", error);
      toast({
        variant: "destructive",
        title: "Mode Switch Failed",
        description: "Failed to switch system mode.",
      });
    } finally {
      setIsSwitching(false);
    }
  };

  // Start/stop services when mode changes externally
  useEffect(() => {
    const syncMode = async () => {
      try {
        if (systemMode === "Full Auto") {
          await stopAimbotAssistance();
          await startAutoTargeting();
        } else if (systemMode === "Manual + Aim-Bot") {
          await stopAutoTargeting();
          await startAimbotAssistance();
        } else {
          await stopAutoTargeting();
          await stopAimbotAssistance();
        }
      } catch (error) {
        console.error("Error syncing mode:", error);
      }
    };
    syncMode();
  }, [systemMode]);

  return (
    <DashboardCard title="System Mode" icon={<Settings />}>
      <div className="flex flex-col gap-3 sm:gap-4">
        <RadioGroup 
          value={systemMode} 
          onValueChange={handleModeChange}
          disabled={isSwitching}
          className="flex flex-col gap-2 sm:gap-3"
        >
          <div className="flex items-center space-x-2 sm:space-x-3 p-2 sm:p-3 rounded-md border border-primary/20 hover:border-primary/40 transition-colors">
            <RadioGroupItem value="Manual" id="manual" className="text-primary border-primary focus:ring-primary"/>
            <Label htmlFor="manual" className="text-primary-foreground/90 font-headline cursor-pointer flex-1 text-sm sm:text-base">
              Manual
            </Label>
          </div>
          <div className="flex items-center space-x-2 sm:space-x-3 p-2 sm:p-3 rounded-md border border-primary/20 hover:border-primary/40 transition-colors">
            <RadioGroupItem value="Manual + Aim-Bot" id="manual-aimbot" className="text-primary border-primary focus:ring-primary"/>
            <Label htmlFor="manual-aimbot" className="text-primary-foreground/90 font-headline cursor-pointer flex-1 text-sm sm:text-base">
              Manual + Aim-Bot
            </Label>
          </div>
          <div className="flex items-center space-x-2 sm:space-x-3 p-2 sm:p-3 rounded-md border border-primary/20 hover:border-primary/40 transition-colors">
            <RadioGroupItem value="Full Auto" id="full-auto" className="text-primary border-primary focus:ring-primary"/>
            <Label htmlFor="full-auto" className="text-primary-foreground/90 font-headline cursor-pointer flex-1 text-sm sm:text-base">
              Full Auto
            </Label>
          </div>
        </RadioGroup>
      </div>
    </DashboardCard>
  );
}

