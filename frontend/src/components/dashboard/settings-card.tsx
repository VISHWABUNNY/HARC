import { Settings, Download, Power } from 'lucide-react';
import { DashboardCard } from '@/components/shared/dashboard-card';
import { Button } from '@/components/ui/button';

export function SettingsCard() {
  return (
    <DashboardCard title="Settings" icon={<Settings />}>
        <div className="space-y-6 flex flex-col justify-between h-full">
            <div className="space-y-2">
                <Button variant="outline" className="w-full">
                    <Download className="mr-2 h-4 w-4" />
                    Export Mission Data
                </Button>
                <Button variant="destructive" className="w-full">
                    <Power className="mr-2 h-4 w-4" />
                    Reset System
                </Button>
            </div>
        </div>
    </DashboardCard>
  );
}
