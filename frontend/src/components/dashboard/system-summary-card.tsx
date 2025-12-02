"use client";

import { useState, useEffect } from "react";
import { BrainCircuit } from "lucide-react";
import { DashboardCard } from "@/components/shared/dashboard-card";
import { getSystemStats, SystemStats } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import type { SystemMode } from "@/app/page";

type SystemSummaryCardProps = {
  systemMode: SystemMode;
};

export function SystemSummaryCard({ systemMode }: SystemSummaryCardProps) {
  const { toast } = useToast();
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await getSystemStats(systemMode);
        setStats(data);
      } catch (error) {
        console.error("Error fetching system stats:", error);
        toast({
          variant: "destructive",
          title: "Error",
          description: "Failed to load system statistics.",
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 2000); // Update every 2 seconds
    return () => clearInterval(interval);
  }, [systemMode, toast]);

  if (isLoading || !stats) {
    return (
      <DashboardCard title="Dashboard" icon={<BrainCircuit />}>
        <div className="space-y-3 sm:space-y-4 text-xs sm:text-sm flex flex-col justify-around h-full">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Loading...</span>
          </div>
        </div>
      </DashboardCard>
    );
  }

  return (
    <DashboardCard title="Dashboard" icon={<BrainCircuit />}>
      <div className="space-y-3 sm:space-y-4 text-xs sm:text-sm flex flex-col justify-around h-full">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Fire Threats Detected:</span>
          <span className="font-mono text-accent">{stats.totalTargetsDetected}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Cannon Readiness:</span>
          <span className={`font-mono font-bold ${stats.cannonReadiness === 'ARMED' ? 'text-destructive' : 'text-green-500'}`}>{stats.cannonReadiness}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">AI Mode:</span>
          <span className="font-mono text-accent">{stats.aiMode}</span>
        </div>
      </div>
    </DashboardCard>
  );
}
