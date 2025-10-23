// src/components/Dashboard.tsx
import { useEffect, useMemo, useState } from "react";
import { api, makeRange } from "../api";
import { useAppStore } from "../store";
import type { KpiSummary, RevenuePoint, TopItem, MixDatum } from "../types";
import KpiSummaryCard from "./KpiSummary";
import WeeklyTrends from "./WeeklyTrends";
import { money } from "../lib/format";

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

  useEffect(() => {
    let alive = true;
    (async () => {
      const [k, t, topItems] = await Promise.all([
        api.kpiSummary({ tenant, date_from, date_to, target: 10000 }),
        api.revenueTrend({ tenant, date_from, date_to }, range),
        api.topItems({ tenant, date_from, date_to, limit: 5 }),
      ]);
      if (!alive) return;
      setKpi(k);
      setTrend(t);

      const food = topItems.filter((x) => x.category === "Food").reduce((s, x) => s + x.revenue, 0);
      const bev = topItems.filter((x) => x.category === "Beverage").reduce((s, x) => s + x.revenue, 0);
      setMix([
        { label: "Food", value: food },
        { label: "Beverage", value: bev },
      ]);
      setTop(topItems);
    })();
    return () => { alive = false; };
  }, [tenant, range, date_from, date_to, tick]);

  return (
    <>
      <section className="card">
        <h3 className="card-title">KPI Summary</h3>
        {kpi && <KpiSummaryCard data={kpi} />}
      </section>

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
                <li key={m.label}>
                  <span>{m.label}</span>
                  <strong>{money(m.value)}</strong>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <section className="card">
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
                  <strong>{money(t.revenue)}</strong>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </>
  );
}
