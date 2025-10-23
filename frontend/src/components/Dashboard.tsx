// frontend/src/components/Dashboard.tsx

import { useEffect, useMemo, useState } from "react";
import {
  api,
  makeRange,
  isZeroKpi,
  isEmpty,
  type KpiSummary,
  type RevenuePoint,
  type TopItem,
  type RangeKey,
} from "../api";
import { demoTrend, demoTop, demoKpi } from "../demo";
import { formatZAR } from "../util/currency";
import { downloadCSV, toCSV } from "../util/csv";
import { useAppStore } from "../store";

// Sibling components (same folder)
import TenantSwitcher from "./TenantSwitcher";
import WeeklyTrends from "./WeeklyTrends";
import KpiSummaryCard from "./KpiSummary";
import HandoverTable from "./HandoverTable";
import Pagination from "./Pagination";
import GuestNotes from "./GuestNotes";
import Incidents from "./Incidents";

type MixDatum = { label: string; value: number };

export default function Dashboard() {
  const { tenant, range, tick } = useAppStore();
  const { date_from, date_to } = useMemo(() => makeRange(range as RangeKey), [range]);

  const [kpi, setKpi] = useState<KpiSummary | null>(null);
  const [trend, setTrend] = useState<RevenuePoint[]>([]);
  const [mix, setMix] = useState<MixDatum[]>([
    { label: "Food", value: 0 },
    { label: "Beverage", value: 0 },
  ]);
  const [top, setTop] = useState<TopItem[]>([]);
  const [updatedAt, setUpdatedAt] = useState<Date | null>(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      const [k, t, topItems] = await Promise.all([
        api.kpiSummary({ tenant, date_from, date_to, target: 10000 }),
        api.revenueTrend({ tenant, date_from, date_to }, range as RangeKey),
        api.topItems({ tenant, date_from, date_to, limit: 5 }),
      ]);

      if (!alive) return;

      const trendData = isEmpty(t) ? demoTrend(date_from, date_to) : t;
      const topData = isEmpty(topItems) ? demoTop : topItems;
      const kpiData = isZeroKpi(k) ? demoKpi(trendData, 10000) : k;

      setTrend(trendData);
      setTop(topData);
      setKpi(kpiData);

      const food = topData
        .filter((x) => x.category === "Food")
        .reduce((s, x) => s + x.revenue, 0);
      const bev = topData
        .filter((x) => x.category === "Beverage")
        .reduce((s, x) => s + x.revenue, 0);

      setMix([
        { label: "Food", value: food },
        { label: "Beverage", value: bev },
      ]);

      setUpdatedAt(new Date());
    })();

    return () => {
      alive = false;
    };
  }, [tenant, range, date_from, date_to, tick]);

  const exportTop = () => {
    if (!top || top.length === 0) return;
    const rows = top.map((t) => ({
      Name: t.name,
      Category: t.category,
      Quantity: t.qty,
      Revenue: t.revenue,
    }));
    downloadCSV(`top-items-${date_from}-to-${date_to}.csv`, toCSV(rows));
  };

  return (
    <>
      {/* Top controls */}
      <div className="controls card">
        <div className="row">
          <div className="brand">
            Legacy Skye <span className="muted">Steward</span>
          </div>
          <div className="grow" />
          <TenantSwitcher />
          <RangeControls />
          <RefreshControls />
        </div>
        <div className="row" style={{ marginTop: 8 }}>
          <div className="muted">
            {updatedAt ? `Last updated ${updatedAt.toLocaleString()}` : "Loading…"}
          </div>
        </div>
      </div>

      {/* KPI summary */}
      <div className="kpi-grid">
        <div className="card">
          {kpi ? (
            <KpiSummaryCard
              data={{
                ...kpi,
                totalFormatted: formatZAR(kpi.total),
                foodFormatted: formatZAR(kpi.food),
                beverageFormatted: formatZAR(kpi.beverage),
                targetFormatted: formatZAR(kpi.target ?? 0),
              }}
            />
          ) : (
            <div className="muted">Loading…</div>
          )}
        </div>
      </div>

      {/* charts row */}
      <div className="grid-2">
        <div className="card">
          <h3 className="card-title">Revenue Trend</h3>
          <WeeklyTrends data={trend} />
        </div>
        <div className="card">
          <h3 className="card-title">Mix (Food vs Beverage)</h3>
          {mix.every((m) => m.value === 0) ? (
            <p className="muted">No mix to show yet.</p>
          ) : (
            <ul className="mix-list">
              {mix.map((m) => (
                <li key={m.label} className="row">
                  <span className="grow">{m.label}</span>
                  <strong>{formatZAR(m.value)}</strong>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* top items */}
      <div className="card">
        <div className="row">
          <h3 className="card-title">Top Items</h3>
          <div className="grow" />
          <button className="btn" onClick={exportTop} disabled={top.length === 0}>
            Export CSV
          </button>
        </div>

        {top.length === 0 ? (
          <p className="muted">No items.</p>
        ) : (
          <div className="top-flex">
            {top.map((t) => (
              <div className="top-chip" key={`${t.name}-${t.category}`} title={`${t.qty} sold`}>
                <div className="top-name">{t.name}</div>
                <div className="top-sub">
                  <span>{t.category}</span>
                  <strong>{formatZAR(t.revenue)}</strong>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* handovers & notes */}
      <div className="grid-2">
        <div className="card">
          <h3 className="card-title">Handovers</h3>
          <HandoverTable />
          <Pagination />
        </div>
        <div className="card">
          <h3 className="card-title">Guest Notes &amp; Incidents</h3>
          <GuestNotes />
          <div className="sp16" />
          <Incidents />
        </div>
      </div>
    </>
  );
}

function RangeControls() {
  const { range, setRange } = useAppStore();
  return (
    <label className="control">
      <span className="label">Range</span>
      <select value={range} onChange={(e) => setRange(e.target.value as RangeKey)}>
        <option value="7d">Last 7 days</option>
        <option value="14d">Last 14 days</option>
        <option value="30d">Last 30 days</option>
      </select>
    </label>
  );
}

function RefreshControls() {
  const { refreshSec, setRefresh } = useAppStore();
  return (
    <label className="control">
      <span className="label">Auto-refresh</span>
      <select value={refreshSec} onChange={(e) => setRefresh(Number(e.target.value))}>
        <option value={15}>15s</option>
        <option value={30}>30s</option>
        <option value={60}>60s</option>
      </select>
    </label>
  );
}
