const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

async function json<T>(url: string) {
  const r = await fetch(url, { next: { revalidate: 0 } });
  if (!r.ok) {
    const text = await r.text().catch(() => "");
    throw new Error(`${r.status} ${r.statusText} - ${text}`);
  }
  return (await r.json()) as T;
}

export type KpiSummary = {
  window: { start: string; end: string };
  current: {
    covers: number;
    food_revenue: number;
    beverage_revenue: number;
    total_revenue: number;
    avg_check: number;
  };
  previous: {
    covers: number;
    food_revenue: number;
    beverage_revenue: number;
    total_revenue: number;
    avg_check: number;
  };
  change_pct: { covers: number; total_revenue: number; avg_check: number };
  target: { total_revenue_target: number; achievement_pct: number };
};

export async function getKpiSummary(target = 10000): Promise<KpiSummary> {
  return json<KpiSummary>(`${BASE}/api/analytics/kpi-summary?target=${encodeURIComponent(target)}`);
}

export async function getTopItems(limit = 10, outlet?: string, start?: string, end?: string) {
  const qs = new URLSearchParams({ limit: String(limit) });
  if (outlet) qs.set("outlet", outlet);
  if (start) qs.set("start_date", start);
  if (end) qs.set("end_date", end);
  return json<Array<{ item: string; count: number }>>(`${BASE}/api/analytics/top-items?${qs.toString()}`);
}

export async function getStaffPraise(limit = 10, outlet?: string, start?: string, end?: string) {
  const qs = new URLSearchParams({ limit: String(limit) });
  if (outlet) qs.set("outlet", outlet);
  if (start) qs.set("start_date", start);
  if (end) qs.set("end_date", end);
  return json<Array<{ staff: string; count: number }>>(`${BASE}/api/analytics/staff-praise?${qs.toString()}`);
}
