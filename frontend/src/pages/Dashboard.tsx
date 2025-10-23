import { useEffect, useMemo, useState } from "react";
import Header from "../components/Header";
import { Card, Stat, ErrorBox } from "../components/ui";
import { AnalyticsAPI } from "../lib/api";
import type { KPISummary, RevenuePoint, TopItem } from "../types";
import { MixChart, RevenueTrend, TopItems } from "../components/Charts";

function formatMoney(n: number) {
  return `$${(n ?? 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
}

export default function Dashboard() {
  const [tenant, setTenant] = useState("legacy");
  const [range, setRange] = useState("7");
  const [autoRefreshSec, setAutoRefreshSec] = useState(30);

  const [kpi, setKpi] = useState<KPISummary | null>(null);
  const [trend, setTrend] = useState<RevenuePoint[] | null>(null);
  const [items, setItems] = useState<TopItem[] | null>(null);

  const [loadingKpi, setLoadingKpi] = useState(false);
  const [loadingTrend, setLoadingTrend] = useState(false);
  const [loadingItems, setLoadingItems] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [dateFrom, dateTo] = useMemo(() => {
    const to = new Date();
    const from = new Date();
    from.setDate(to.getDate() - (parseInt(range, 10) - 1));
    const iso = (d: Date) => d.toISOString().slice(0, 10);
    return [iso(from), iso(to)] as const;
  }, [range]);

  const load = async () => {
    setError(null);
    try {
      setLoadingKpi(true);
      setLoadingTrend(true);
      setLoadingItems(true);

      const [kpiRes, trendRes, itemsRes] = await Promise.all([
        AnalyticsAPI.kpiSummary(dateFrom, dateTo, 10_000),
        AnalyticsAPI.revenueTrend(dateFrom, dateTo),
        AnalyticsAPI.topItems(5, dateFrom, dateTo),
      ]);

      setKpi(kpiRes);
      setTrend(trendRes);
      setItems(itemsRes);
    } catch (e: any) {
      setError(e.message || "Failed to load analytics.");
    } finally {
      setLoadingKpi(false);
      setLoadingTrend(false);
      setLoadingItems(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tenant, range]);

  useEffect(() => {
    if (!autoRefreshSec) return;
    const id = setInterval(load, autoRefreshSec * 1000);
    return () => clearInterval(id);
  }, [autoRefreshSec, dateFrom, dateTo]);

  const progressPct = Math.round((kpi?.progress ?? 0) * 100);

  return (
    <div className="mx-auto max-w-7xl space-y-4 p-4">
      <Header
        tenant={tenant}
        setTenant={setTenant}
        range={range}
        setRange={setRange}
        autoRefreshSec={autoRefreshSec}
        setAutoRefreshSec={setAutoRefreshSec}
        onRefresh={load}
      />

      {error ? <ErrorBox message={error} /> : null}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Stat
          label="Total Revenue"
          value={formatMoney(kpi?.total ?? 0)}
          sub={`${progressPct}% of target`}
          progress={progressPct}
        />
        <Stat label="Food" value={formatMoney(kpi?.food ?? 0)} sub={`${kpi?.food ? Math.round(((kpi?.food ?? 0) / (kpi?.total || 1)) * 100) : 0}%`} />
        <Stat label="Beverage" value={formatMoney(kpi?.beverage ?? 0)} sub={`${kpi?.beverage ? Math.round(((kpi?.beverage ?? 0) / (kpi?.total || 1)) * 100) : 0}%`} />
        <Stat label="Target" value={formatMoney(kpi?.target ?? 10_000)} sub={`${progressPct}%`} />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <RevenueTrend data={trend} loading={loadingTrend} />
        </div>
        <div className="lg:col-span-1">
          <MixChart
            food={kpi?.food ?? 0}
            beverage={kpi?.beverage ?? 0}
            loading={loadingKpi}
          />
        </div>
      </div>

      <TopItems data={items} loading={loadingItems} />

      <Card>
        <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-white/50">
          <div>
            Tenant: <span className="text-white/70">{tenant}</span> • Range:{" "}
            <span className="text-white/70">{range}d</span> • Auto-refresh:{" "}
            <span className="text-white/70">{autoRefreshSec ? `${autoRefreshSec}s` : "Off"}</span>
          </div>
          <div>© {new Date().getFullYear()} Legacy Skye • Steward</div>
        </div>
      </Card>
    </div>
  );
}
