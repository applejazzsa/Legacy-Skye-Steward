// src/components/KpiSummary.tsx
import type { KpiSummary } from "../types";
import { money, pct } from "../lib/format";

export default function KpiSummaryCard({ data }: { data: KpiSummary }) {
  const progress = data.target > 0 ? data.total / data.target : 0;

  return (
    <div className="kpi four">
      <div className="kpi-card">
        <div className="kpi-label">Total Revenue</div>
        <div className="kpi-value">{money(data.total)}</div>
        <div className="kpi-sub">{pct(progress)} of target</div>
      </div>
      <div className="kpi-card">
        <div className="kpi-label">Food</div>
        <div className="kpi-value">{money(data.food)}</div>
        <div className="kpi-sub">{pct(data.total ? data.food / data.total : 0)}</div>
      </div>
      <div className="kpi-card">
        <div className="kpi-label">Beverage</div>
        <div className="kpi-value">{money(data.beverage)}</div>
        <div className="kpi-sub">{pct(data.total ? data.beverage / data.total : 0)}</div>
      </div>
      <div className="kpi-card">
        <div className="kpi-label">Target</div>
        <div className="kpi-value">{money(data.target)}</div>
        <div className="kpi-sub">{pct(progress)}</div>
      </div>
    </div>
  );
}
