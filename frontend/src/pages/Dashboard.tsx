import React, { useEffect, useState } from "react";
import { api, KpiSummary, TopItem } from "../lib/api";

function Card({ title, value, sub }: { title: string; value: React.ReactNode; sub?: string }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-card dark:bg-slate-900 dark:border-slate-700">
      <div className="text-[11px] uppercase tracking-[0.18em] text-slate-500">{title}</div>
      <div className="mt-2 text-3xl font-semibold">{value}</div>
      {sub ? <div className="mt-1 text-sm text-slate-500">{sub}</div> : null}
    </div>
  );
}

export default function Dashboard() {
  const [kpi, setKpi] = useState<KpiSummary | null>(null);
  const [top, setTop] = useState<TopItem[]>([]);
  const [incidentsOpen, setIncidentsOpen] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    const ac = new AbortController();
    Promise.all([
      api.kpiSummary(10000, ac.signal).then(setKpi),
      api.topItems(1, ac.signal).then(setTop),
      api.incidents(ac.signal).then((rows) => setIncidentsOpen(rows.filter(r => r.status?.toLowerCase() !== "resolved").length)),
    ])
      .catch((e) => setErr(e.message))
      .finally(() => setLoading(false));
    return () => ac.abort();
  }, []);

  return (
    <>
      <section className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <Card title="Total Covers (7d)" value={loading ? "…" : (kpi?.covers ?? "—")} sub="From /api/analytics/kpi-summary" />
        <Card title="Revenue (7d)" value={loading ? "…" : (kpi ? `£${(kpi.revenue).toLocaleString()}` : "—")} sub="Food + Beverage" />
        <Card title="Incidents Open" value={loading ? "…" : (incidentsOpen ?? "—")} sub="From /api/incidents" />
        <Card title="Top Seller" value={loading ? "…" : (top[0]?.name ?? "—")} sub="From /api/analytics/top-items" />
      </section>

      {err ? (
        <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-200">
          Failed to load data: {err}
        </div>
      ) : null}

      <section className="mt-6 grid grid-cols-1 xl:grid-cols-3 gap-4">
        <RecentHandovers />
        <LatestGuestNotes />
      </section>
    </>
  );
}

function RecentHandovers() {
  const [rows, setRows] = useState<any[]>([]);
  useEffect(() => {
    const ac = new AbortController();
    api.handovers(ac.signal).then(setRows).catch(() => {});
    return () => ac.abort();
  }, []);
  return (
    <div className="xl:col-span-2 rounded-2xl border border-slate-200 bg-white p-4 dark:bg-slate-900 dark:border-slate-700">
      <div className="mb-2 text-sm font-semibold text-slate-700">Recent Handovers</div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="text-slate-500">
            <tr><th className="text-left py-2 pr-4">Date</th><th className="text-left py-2 pr-4">Outlet</th><th className="text-left py-2 pr-4">Shift</th><th className="text-right py-2">Covers</th></tr>
          </thead>
          <tbody>
            {rows.slice(0, 6).map(r => (
              <tr key={r.id} className="border-t border-slate-100 dark:border-slate-800">
                <td className="py-2 pr-4">{new Date(r.date).toLocaleString()}</td>
                <td className="py-2 pr-4">{r.outlet}</td>
                <td className="py-2 pr-4">{r.shift}</td>
                <td className="py-2 text-right">{r.covers}</td>
              </tr>
            ))}
            {!rows.length && (
              <tr><td className="py-3 text-slate-500" colSpan={4}>No handovers yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function LatestGuestNotes() {
  const [rows, setRows] = useState<any[]>([]);
  useEffect(() => {
    const ac = new AbortController();
    api.guestNotes(ac.signal).then(setRows).catch(() => {});
    return () => ac.abort();
  }, []);
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 dark:bg-slate-900 dark:border-slate-700">
      <div className="mb-2 text-sm font-semibold text-slate-700">Latest Guest Notes</div>
      <ul className="space-y-2">
        {rows.slice(0, 6).map(r => (
          <li key={r.id} className="rounded-xl border border-slate-200 p-2 dark:border-slate-800">
            <div className="text-sm font-medium">{r.guest_name}</div>
            <div className="text-sm text-slate-600 dark:text-slate-300">{r.note}</div>
            <div className="text-xs text-slate-400 mt-1">{new Date(r.created_at).toLocaleString()}</div>
          </li>
        ))}
        {!rows.length && <li className="text-sm text-slate-500">No guest notes yet.</li>}
      </ul>
    </div>
  );
}
