"use client";

import { useEffect, useState } from 'react';
import { Activity } from 'lucide-react';
import { DashboardCard } from '@/components/shared/dashboard-card';
import { getSystemVitals, SystemVitals } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

const CircularProgress = ({ value, label, unit }: { value: number; label: string; unit: string; }) => {
  const radius = 30;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;
  const size = 64;

  return (
    <div className="flex flex-col items-center">
      <svg className="w-16 h-16 sm:w-20 sm:h-20 md:w-24 md:h-24 transform -rotate-90" viewBox={`0 0 ${size} ${size}`}>
        <circle
          className="text-primary/20"
          stroke="currentColor"
          strokeWidth="4"
          fill="transparent"
          r={radius}
          cx={size / 2}
          cy={size / 2}
        />
        <circle
          className="text-accent"
          stroke="currentColor"
          strokeWidth="4"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          fill="transparent"
          r={radius}
          cx={size / 2}
          cy={size / 2}
          style={{ transition: 'stroke-dashoffset 0.3s' }}
        />
      </svg>
      <div className="text-center -mt-12 sm:-mt-14 md:-mt-16">
        <p className="font-mono text-base sm:text-lg md:text-xl text-primary-foreground">{value.toFixed(1)}<span className="text-xs sm:text-sm">{unit}</span></p>
        <p className="text-[10px] sm:text-xs text-muted-foreground uppercase">{label}</p>
      </div>
    </div>
  );
};

export function DiagnosticsCard() {
    const { toast } = useToast();
    const [vitals, setVitals] = useState<SystemVitals | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchVitals = async () => {
            try {
                const data = await getSystemVitals();
                setVitals(data);
            } catch (error) {
                console.error("Error fetching system vitals:", error);
                toast({
                    variant: "destructive",
                    title: "Error",
                    description: "Failed to load system diagnostics.",
                });
            } finally {
                setIsLoading(false);
            }
        };

        fetchVitals();
        const interval = setInterval(fetchVitals, 1000); // Update every second
        return () => clearInterval(interval);
    }, [toast]);

    const formatUptime = (totalSeconds: number) => {
        const d = Math.floor(totalSeconds / 86400);
        const h = Math.floor((totalSeconds % 86400) / 3600);
        const m = Math.floor((totalSeconds % 3600) / 60);
        return `${d}d ${h.toString().padStart(2, '0')}h ${m.toString().padStart(2, '0')}m`;
    }

    if (isLoading || !vitals) {
        return (
            <DashboardCard title="Diagnostics" icon={<Activity />}>
                <div className="flex flex-col justify-center items-center h-full">
                    <p className="text-muted-foreground">Loading...</p>
                </div>
            </DashboardCard>
        );
    }

  return (
    <DashboardCard title="Diagnostics" icon={<Activity />}>
      <div className="flex flex-col justify-between h-full">
        <div className="grid grid-cols-3 gap-2 sm:gap-3 md:gap-4 text-center">
            <CircularProgress value={vitals.cpuTemp} label="CPU Temp" unit="°C" />
            <CircularProgress value={vitals.gpuTemp} label="GPU Temp" unit="°C" />
            <CircularProgress value={vitals.motorCurrent * 10} label="Motor" unit="A" />
        </div>
        <div className="mt-4 sm:mt-6 text-center border-t-2 border-primary/20 pt-3 sm:pt-4">
            <p className="text-xs sm:text-sm text-muted-foreground uppercase">System Uptime</p>
            <p className="font-mono text-lg sm:text-xl md:text-2xl text-accent">{formatUptime(vitals.uptime)}</p>
        </div>
      </div>
    </DashboardCard>
  );
}
