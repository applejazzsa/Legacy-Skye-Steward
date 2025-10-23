// src/components/Toolbar.tsx
import TenantSwitcher from "./TenantSwitcher";

export type ToolbarState = {
  tenant: string;
  from: string; // yyyy-mm-dd
  to: string; // yyyy-mm-dd
  outletQuery: string;
  autoRefresh: boolean;
  refreshMs: number;
};

type Props = {
  state: ToolbarState;
  onChange: (patch: Partial<ToolbarState>) => void;
};

export default function Toolbar({ state, onChange }: Props) {
  return (
    <div className="flex flex-col md:flex-row md:items-center gap-3">
      <TenantSwitcher
        value={state.tenant}
        onChange={(tenant) => onChange({ tenant })}
      />

      <div className="flex items-center gap-2">
        <label className="text-sm font-medium">From</label>
        <input
          type="date"
          className="border rounded px-2 py-1 text-sm"
          value={state.from}
          onChange={(e) => onChange({ from: e.target.value })}
        />
        <label className="text-sm font-medium">To</label>
        <input
          type="date"
          className="border rounded px-2 py-1 text-sm"
          value={state.to}
          onChange={(e) => onChange({ to: e.target.value })}
        />
      </div>

      <div className="flex items-center gap-2">
        <input
          placeholder="Filter by outlet…"
          className="border rounded px-2 py-1 text-sm w-44"
          value={state.outletQuery}
          onChange={(e) => onChange({ outletQuery: e.target.value })}
        />
      </div>

      <div className="flex items-center gap-2 md:ml-auto">
        <label className="text-sm font-medium">Auto-refresh</label>
        <input
          type="checkbox"
          checked={state.autoRefresh}
          onChange={(e) => onChange({ autoRefresh: e.target.checked })}
        />
        <select
          className="border rounded px-2 py-1 text-sm"
          value={String(state.refreshMs)}
          onChange={(e) => onChange({ refreshMs: Number(e.target.value) })}
          disabled={!state.autoRefresh}
        >
          <option value={15000}>15s</option>
          <option value={30000}>30s</option>
          <option value={60000}>60s</option>
        </select>
      </div>
    </div>
  );
}
