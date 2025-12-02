"use client";

import { useState, useEffect } from 'react';
import { getSystemLogs, SystemLog } from '@/lib/api';

const FooterConsole = () => {
  const [logs, setLogs] = useState<SystemLog[]>([]);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const data = await getSystemLogs("ALL", 20); // Get last 20 logs for ticker
        setLogs(data);
      } catch (error) {
        console.error("Error fetching logs for footer:", error);
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 3000); // Update every 3 seconds
    return () => clearInterval(interval);
  }, []);

  const tickerText = logs.map(log => `[${log.timestamp}] :: ${log.category} :: ${log.message}`).join(' +++ ');

  return (
    <footer className="fixed bottom-0 left-0 right-0 z-50 h-7 sm:h-8 bg-black/80 backdrop-blur-sm border-t border-primary/20 overflow-hidden">
      <div className="w-full h-full flex items-center">
        <p className="font-code text-[10px] sm:text-xs text-primary whitespace-nowrap animate-ticker">
          {tickerText || "System initializing..."}
        </p>
      </div>
    </footer>
  );
};

export default FooterConsole;
