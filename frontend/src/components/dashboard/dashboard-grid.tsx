import { SystemSummaryCard } from "./system-summary-card";
import { WeaponControlCard } from "./weapon-control-card";
import { LiveFeedCard } from "./live-feed-card";
import { SystemLogsCard } from "./system-logs-card";
import { DiagnosticsCard } from "./diagnostics-card";
import { ModeSelectorCard } from "./mode-selector-card";
import type { SystemMode } from "@/app/page";

type DashboardGridProps = {
  systemMode: SystemMode;
  setSystemMode: (mode: SystemMode) => void;
};

const DashboardGrid = ({ systemMode, setSystemMode }: DashboardGridProps) => {
  return (
    <div className="flex flex-col gap-3 sm:gap-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4">
          <div className="flex flex-col gap-3 sm:gap-4 md:col-span-1">
              <SystemSummaryCard systemMode={systemMode} />
              <DiagnosticsCard />
          </div>
          <div className="md:col-span-2 lg:col-span-3 flex flex-col gap-3 sm:gap-4">
              <LiveFeedCard systemMode={systemMode} />
          </div>
          <div className="flex flex-col gap-3 sm:gap-4 md:col-span-2 lg:col-span-1">
              <ModeSelectorCard systemMode={systemMode} setSystemMode={setSystemMode} />
              <WeaponControlCard systemMode={systemMode} />
          </div>
      </div>
      <div className="col-span-1 md:col-span-2 lg:col-span-5">
        <SystemLogsCard />
      </div>
    </div>
  );
};

export default DashboardGrid;
