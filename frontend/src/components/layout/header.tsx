'use client';

import { useState, useEffect } from 'react';
import { Target } from 'lucide-react';
import { HarcLogo } from '@/components/shared/icons';
import { getSystemStatus } from '@/lib/api';

const Header = () => {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    const checkSystemStatus = async () => {
      try {
        const status = await getSystemStatus();
        setIsOnline(status.isOnline);
      } catch (error) {
        console.error("Error checking system status:", error);
        setIsOnline(false);
      }
    };

    // Check system status from backend
    checkSystemStatus();
    const interval = setInterval(checkSystemStatus, 3000); // Check every 3 seconds

    // Also check browser online status
    const handleOnlineStatus = () => {
      const browserOnline = navigator.onLine;
      if (browserOnline) {
        checkSystemStatus(); // Re-check backend when browser comes online
      } else {
        setIsOnline(false);
      }
    };
    
    window.addEventListener('online', handleOnlineStatus);
    window.addEventListener('offline', handleOnlineStatus);

    return () => {
      clearInterval(interval);
      window.removeEventListener('online', handleOnlineStatus);
      window.removeEventListener('offline', handleOnlineStatus);
    };
  }, []);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-sm border-b border-primary/20">
      <div className="container mx-auto flex h-14 sm:h-16 items-center justify-between px-2 sm:px-4">
        <div className="flex items-center gap-2 sm:gap-4">
          <HarcLogo className="h-5 w-auto sm:h-6 text-primary" />
        </div>
        
        <div className="flex items-center gap-2 sm:gap-6 text-xs sm:text-sm">
          <div className="flex items-center gap-1 sm:gap-2">
            {isOnline ? <Target className="h-3 w-3 sm:h-4 sm:w-4 text-green-500" /> : <Target className="h-3 w-3 sm:h-4 sm:w-4 text-destructive" />}
            <span className={`font-mono uppercase ${isOnline ? 'text-green-500' : 'text-destructive'} hidden sm:inline`}>
              {isOnline ? 'CANNON ONLINE' : 'CANNON OFFLINE'}
            </span>
            <span className={`font-mono uppercase ${isOnline ? 'text-green-500' : 'text-destructive'} sm:hidden`}>
              {isOnline ? 'ONLINE' : 'OFFLINE'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
