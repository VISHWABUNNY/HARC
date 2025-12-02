"use client";

import { useState, useEffect } from 'react';
import { FileText } from 'lucide-react';
import { DashboardCard } from '@/components/shared/dashboard-card';
import { getSystemLogs, SystemLog } from '@/lib/api';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';

type LogCategory = "ALL" | "SYSTEM" | "CANNON" | "AI";

export function SystemLogsCard() {
  const { toast } = useToast();
  const [filter, setFilter] = useState<LogCategory>("ALL");
  const [logs, setLogs] = useState<SystemLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const data = await getSystemLogs(filter === "ALL" ? "ALL" : filter, 50);
        setLogs(data);
      } catch (error) {
        console.error("Error fetching system logs:", error);
        toast({
          variant: "destructive",
          title: "Error",
          description: "Failed to load system logs.",
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 2000); // Update every 2 seconds
    return () => clearInterval(interval);
  }, [filter, toast]);

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'SYSTEM': return 'text-blue-400';
      case 'CANNON': return 'text-yellow-400';
      case 'AI': return 'text-purple-400';
      default: return 'text-primary-foreground';
    }
  };

  return (
    <DashboardCard title="System Logs" icon={<FileText />} cardContentClassName="flex flex-col">
      <div className="flex-shrink-0 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 mb-2">
          <span className="text-xs text-muted-foreground">Filter by:</span>
          <div className="flex gap-1 flex-wrap">
              {(['ALL', 'SYSTEM', 'CANNON', 'AI'] as LogCategory[]).map(cat => (
                  <Button key={cat} onClick={() => setFilter(cat)} size="sm" variant={filter === cat ? "destructive" : "ghost"} className="h-6 px-2 text-[10px] sm:text-xs">
                      {cat}
                  </Button>
              ))}
          </div>
      </div>
      <ScrollArea className="flex-grow h-48 sm:h-64 pr-2 sm:pr-4">
        <div className="font-code text-[10px] sm:text-xs space-y-1">
          {isLoading ? (
            <p className="text-muted-foreground">Loading logs...</p>
          ) : logs.length === 0 ? (
            <p className="text-muted-foreground">No logs available</p>
          ) : (
            logs.map((log, index) => (
              <p key={index} className="whitespace-pre-wrap">
                <span className="text-muted-foreground">{log.timestamp}</span>
                <span className={`font-bold mx-2 ${getCategoryColor(log.category)}`}>[{log.category}]</span>
                <span>{log.message}</span>
              </p>
            ))
          )}
        </div>
      </ScrollArea>
    </DashboardCard>
  );
}
