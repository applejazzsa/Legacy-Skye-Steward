import KpiCard from "../components/KpiCard";
import ListCard from "../components/ListCard";
import HandoversTable from "../components/HandoversTable";
import {
  fetchHandovers,
  fetchKpiSummary,
  fetchStaffPraise,
  fetchTopItems,
} from "../lib/api";

const KPI_TARGET = 10000;

export default async function DashboardPage() {
  const [kpiSummary, topItems, staffPraise, handovers] = await Promise.all([
    fetchKpiSummary(KPI_TARGET),
    fetchTopItems(5),
    fetchStaffPraise(5),
    fetchHandovers(10),
  ]);

  const kpiCards = [
    {
      title: "Total Revenue",
      current: kpiSummary.current.total_revenue,
      previous: kpiSummary.previous.total_revenue,
      change: kpiSummary.change_pct.total_revenue,
      format: "currency" as const,
    },
    {
      title: "Covers",
      current: kpiSummary.current.covers,
      previous: kpiSummary.previous.covers,
      change: kpiSummary.change_pct.covers,
      format: "number" as const,
    },
    {
      title: "Average Check",
      current: kpiSummary.current.avg_check,
      previous: kpiSummary.previous.avg_check,
      change: kpiSummary.change_pct.avg_check,
      format: "currency" as const,
    },
    {
      title: "Target Achievement",
      current: kpiSummary.target.achievement_pct,
      previous: 100,
      change: kpiSummary.target.achievement_pct - 100,
      format: "number" as const,
    },
  ];

  const topItemEntries = topItems.map((item) => ({
    label: item.item,
    value: item.count.toString(),
  }));

  const staffPraiseEntries = staffPraise.map((entry) => ({
    label: entry.staff,
    value: entry.count.toString(),
  }));

  return (
    <main className="px-6 py-10">
      <div className="mx-auto max-w-6xl space-y-8">
        <header className="space-y-2">
          <h1 className="text-3xl font-semibold text-slate-900">Handover &amp; Analytics</h1>
          <p className="text-sm text-slate-600">
            Monitor daily performance, celebrate your team, and spot trends across outlets.
          </p>
        </header>

        <section className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          {kpiCards.map((card) => (
            <KpiCard key={card.title} {...card} />
          ))}
        </section>

        <section className="grid gap-6 lg:grid-cols-[2fr,1fr]">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-slate-900">Recent Handovers</h2>
              <span className="text-xs uppercase tracking-wide text-slate-500">
                Latest 10 entries
              </span>
            </div>
            <HandoversTable handovers={handovers} />
          </div>

          <div className="grid gap-6">
            <ListCard title="Top Items" items={topItemEntries} emptyMessage="No sales recorded" />
            <ListCard title="Staff Praise" items={staffPraiseEntries} emptyMessage="No notes yet" />
          </div>
        </section>
      </div>
    </main>
  );
}
