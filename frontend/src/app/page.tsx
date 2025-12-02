'use client';

import { useState } from 'react';
import Header from '@/components/layout/header';
import FooterConsole from '@/components/layout/footer-console';
import DashboardGrid from '@/components/dashboard/dashboard-grid';

export type SystemMode = "Manual" | "Full Auto";

export default function Home() {
  const [systemMode, setSystemMode] = useState<SystemMode>('Manual');
  
  return (
    <div className="relative min-h-screen bg-black font-headline text-primary-foreground selection:bg-accent selection:text-black">
      <Header />
      <main className="pt-14 sm:pt-20 pb-20 sm:pb-12 px-2 sm:px-4 md:px-6 lg:px-8">
        <DashboardGrid systemMode={systemMode} setSystemMode={setSystemMode} />
      </main>
      <FooterConsole />
    </div>
  );
}
