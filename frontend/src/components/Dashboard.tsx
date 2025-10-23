// frontend/src/components/Dashboard.tsx
import { useEffect, useMemo, useState } from "react";
import { api, makeRange, isZeroKpi, isEmpty } from "../api";
import type { KpiSummary, RevenuePoint, TopItem, MixDatum } from "../types";

import KpiSummaryCard from "../KpiSummary";
import WeeklyTrends from "../WeeklyTrends";
import TenantSwitcher from "../TenantSwitcher";
import Pagination from "../Pagination";
import CommandPalette from "../CommandPalette";
import HandoverTable from "../HandoverTable";
import GuestNotes from "../GuestNotes";
import Incidents from "../Incidents";

import { demoTrend, demoTop, demoKpi } from "../demo";
import { useAppStore } from "../store";
import { formatZAR } from "../util/currency";

export default function Dashboard() {
  const { tenant, range, tick } = useAppStore();
  const { date_from, date_to } = useMemo(() => makeRange(range), [range]);

  const [kpi, setKpi] = useState<KpiSummary | null>(null);
  const [trend, setTrend] = useState<RevenuePoint[]>([]);
  const [mix, setMix] = useState<MixDatum[]>([
    { label: "Food", value: 0 },
    { label: "Beverage", value: 0 },
  ]);
  const [top, setTop] = useState<TopItem[]>([]);

  // Fetch on mount + when tenant/range/auto-tick changes
  useEffect(() => {
    let alive = true;
    (async () => {
      const [k, t, topItems] = await Promise.all([
        api.kpiSummary({ tenant, date_from, date_to, target: 10000 }),
        api.revenueTrend({ tenant, date_from, date_to }, range),
        api.topItems({ tenant, date_from, date_to, limit: 5 }),
      ]);

      if (!alive) return;

      // trend fallback
      const trendData = isEmpty(t) ? demoTrend(date_from, date_to) : t;

      // top items fallback
      const topData = isEmpty(topItems) ? demoTop : topItems;

      // kpi fallback
      const kpiComputed = isZeroKpi(k) ? demoKpi(trendData, 10000) : k;

      setKpi(kpiComputed);
      setTrend(trendData);

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
      setTop(topData);
    })();
    return () => {
      alive = false;
    };
  }, [tenant, range, date_from, date_to, tick]);

  return (
    <>
      <CommandPalette />

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
      </div>

      <div className="kpi-grid">
        <div className="card">
          {kpi ? (
            <KpiSummaryCard data={kpi} currencyFormatter={formatZAR} />
          ) : (
            <div className="muted">Loading...</div>
          )}
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <h3 className="card-title">Revenue Trend</h3>
          <WeeklyTrends data={trend} currencyFormatter={formatZAR} />
        </div>

        <div className="card">
          <h3 className="card-title">Mix (Food vs Beverage)</h3>
          {mix.every((m) => m.value === 0) ? (
            <p className="muted">No mix to show yet.</p>
          ) : (
            <ul className="mix-list">
              {mix.map((m) => (
                <li key={m.label}>
                  <span>{m.label}</span>
                  <strong>{formatZAR(m.value)}</strong>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="card">
        <h3 className="card-title">Top Items</h3>
        {top.length === 0 ? (
          <p className="muted">No items.</p>
        ) : (
          <div className="top-flex">
            {top.map((t) => (
              <div className="top-chip" key={t.name} title={`${t.qty} sold`}>
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

      <div className="grid-2">
        <div className="card">
          <h3 className="card-title">Handovers</h3>
          <HandoverTable />
          <Pagination />
        </div>
        <div className="card">
          <h3 className="card-title">Guest Notes & Incidents</h3>
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
      <select value={range} onChange={(e) => setRange(e.target.value as any)}>
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
      <select
        value={refreshSec}
        onChange={(e) => setRefresh(Number(e.target.value))}
      >
        <option value={15}>15s</option>
        <option value={30}>30s</option>
        <option value={60}>60s</option>
      </select>
    </label>
  );
}
