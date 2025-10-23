import type { DateRange, KpiSummary, RevenuePoint, TopItem } from "./types";

const BASE = "/api/analytics";

function asJson<T>(res: Response): Promise<T> {
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

export function makeRange(range: "7d" | "14d" | "30d"): DateRange {
  const to = new Date();
  const days = range === "30d" ? 30 : range === "14d" ? 14 : 7;
  const from = new Date(to);
  from.setDate(to.getDate() - (days - 1));
  const fmt = (d: Date) => d.toISOString().slice(0, 10);
  return { date_from: fmt(from), date_to: fmt(to) };
}

type TenantParam = { tenant?: string | null };

export const api = {
  async kpiSummary(
    p: TenantParam & { target?: number } & DateRange
  ): Promise<KpiSummary> {
    const u = new URL(`${BASE}/kpi-summary`, window.location.origin);
    if (p.tenant) u.searchParams.set("tenant", String(p.tenant));
    u.searchParams.set("date_from", p.date_from);
    u.searchParams.set("date_to", p.date_to);
    if (p.target != null) u.searchParams.set("target", String(p.target));
    return fetch(u.toString(), { credentials: "include" }).then(asJson);
  },

  async revenueTrend(
    p: TenantParam & DateRange,
    _range: string
  ): Promise<RevenuePoint[]> {
    const u = new URL(`${BASE}/revenue-trend`, window.location.origin);
    if (p.tenant) u.searchParams.set("tenant", String(p.tenant));
    u.searchParams.set("date_from", p.date_from);
    u.searchParams.set("date_to", p.date_to);
    return fetch(u.toString(), { credentials: "include" }).then(asJson);
  },

  async topItems(
    p: TenantParam & DateRange & { limit?: number }
  ): Promise<TopItem[]> {
    const u = new URL(`${BASE}/top-items`, window.location.origin);
    if (p.tenant) u.searchParams.set("tenant", String(p.tenant));
    u.searchParams.set("date_from", p.date_from);
    u.searchParams.set("date_to", p.date_to);
    u.searchParams.set("limit", String(p.limit ?? 5));
    return fetch(u.toString(), { credentials: "include" }).then(asJson);
  },
};
