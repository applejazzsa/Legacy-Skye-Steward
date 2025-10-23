import { Button } from "./ui";

type Props = {
  tenant: string;
  setTenant: (t: string) => void;
  range: string;
  setRange: (r: string) => void;
  autoRefreshSec: number;
  setAutoRefreshSec: (n: number) => void;
  onRefresh: () => void;
};

const ranges = [
  { v: "7", label: "Last 7 days" },
  { v: "14", label: "Last 14 days" },
  { v: "30", label: "Last 30 days" },
];

export default function Header({
  tenant,
  setTenant,
  range,
  setRange,
  autoRefreshSec,
  setAutoRefreshSec,
  onRefresh,
}: Props) {
  return (
    <div className="sticky top-0 z-20 -mx-4 mb-2 bg-[#0b0f14]/70 px-4 py-3 backdrop-blur">
      <div className="mx-auto flex max-w-7xl flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="text-xl font-semibold tracking-tight">Legacy Skye</div>
          <span className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-2 py-0.5 text-xs text-emerald-200">
            Steward
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <label className="flex items-center gap-2 text-sm text-white/70">
            Tenant
            <select
              value={tenant}
              onChange={(e) => setTenant(e.target.value)}
              className="h-8 rounded-lg border border-white/10 bg-black/30 px-2 text-sm outline-none"
            >
              <option value="legacy">legacy</option>
            </select>
          </label>

          <label className="ml-1 flex items-center gap-2 text-sm text-white/70">
            Range
            <select
              value={range}
              onChange={(e) => setRange(e.target.value)}
              className="h-8 rounded-lg border border-white/10 bg-black/30 px-2 text-sm outline-none"
            >
              {ranges.map((r) => (
                <option key={r.v} value={r.v}>
                  {r.label}
                </option>
              ))}
            </select>
          </label>

          <label className="ml-1 flex items-center gap-2 text-sm text-white/70">
            Auto-refresh
            <select
              value={String(autoRefreshSec)}
              onChange={(e) => setAutoRefreshSec(Number(e.target.value))}
              className="h-8 rounded-lg border border-white/10 bg-black/30 px-2 text-sm outline-none"
            >
              <option value="0">Off</option>
              <option value="15">15s</option>
              <option value="30">30s</option>
              <option value="60">60s</option>
            </select>
          </label>

          <Button onClick={onRefresh} className="ml-1 h-8">
            Refresh
          </Button>
        </div>
      </div>
    </div>
  );
}
