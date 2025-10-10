import { getKpiSummary, getTopItems, getStaffPraise } from "@/lib/api";

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-2xl border p-4 shadow-sm bg-white">
      <div className="text-sm text-gray-500">{label}</div>
      <div className="text-2xl font-semibold">{value}</div>
    </div>
  );
}

export default async function Page() {
  const [kpi, topItems, praise] = await Promise.all([
    getKpiSummary(10000),
    getTopItems(10),
    getStaffPraise(10),
  ]);

  return (
    <main className="mx-auto max-w-5xl p-6 space-y-8">
      <h1 className="text-3xl font-bold">Legacy Skye Steward — Dashboard</h1>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">KPI Summary</h2>
        <div className="text-sm text-gray-500">
          Window: {kpi.window.start} → {kpi.window.end}
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Stat label="Total Revenue" value={kpi.current.total_revenue.toFixed(2)} />
          <Stat label="Covers" value={kpi.current.covers} />
          <Stat label="Avg Check" value={kpi.current.avg_check.toFixed(2)} />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Stat label="Target" value={kpi.target.total_revenue_target.toFixed(0)} />
          <Stat label="Achievement %" value={`${kpi.target.achievement_pct.toFixed(2)}%`} />
          <Stat label="Revenue Δ%" value={`${kpi.change_pct.total_revenue.toFixed(2)}%`} />
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Top Items</h2>
        {topItems.length === 0 ? (
          <div className="text-gray-500 text-sm">No item data in the selected window.</div>
        ) : (
          <ul className="divide-y rounded-2xl border bg-white">
            {topItems.map((t, i) => (
              <li key={i} className="flex items-center justify-between p-3">
                <span>{t.item}</span>
                <span className="text-gray-500">{t.count}</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Staff Praise</h2>
        {praise.length === 0 ? (
          <div className="text-gray-500 text-sm">No guest praise data yet.</div>
        ) : (
          <ul className="divide-y rounded-2xl border bg-white">
            {praise.map((p, i) => (
              <li key={i} className="flex items-center justify-between p-3">
                <span>{p.staff}</span>
                <span className="text-gray-500">{p.count}</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
