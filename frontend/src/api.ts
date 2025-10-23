// frontend/src/api.ts

export type RangeKey = "7d" | "14d" | "30d";

export type KpiSummary = {
  total: number;
  food: number;
  beverage: number;
  target?: number;
  target_pct?: number; // 0–100
};

export type RevenuePoint = {
  d: string; // YYYY-MM-DD
  t: number; // total for the day
};

export type TopItem = {
  name: string;
  category: "Food" | "Beverage" | string;
  qty: number;
  revenue: number;
};

const API_BASE =
  (import.meta as any).env?.VITE_API_BASE ||
  "http://127.0.0.1:8000";

const json = (r: Response) => {
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json();
};

/** Build date range from a quick preset */
export function makeRange(range: RangeKey) {
  const to = new Date();
  const from = new Date();
  if (range === "7d") from.setDate(to.getDate() - 6);
  if (range === "14d") from.setDate(to.getDate() - 13);
  if (range === "30d") from.setDate(to.getDate() - 29);
  const date_from = from.toISOString().slice(0, 10);
  const date_to = to.toISOString().slice(0, 10);
  return { date_from, date_to };
}

/** Small helpers for safe fallbacks */
export const isZeroKpi = (k?: any) =>
  !k || [k.total, k.food, k.beverage].every((v) => !v || v === 0);

export const isEmpty = (arr?: any[]) => !arr || arr.length === 0;

type CommonParams = {
  tenant?: string;
  date_from: string;
  date_to: string;
};

export const api = {
  async kpiSummary(params: CommonParams & { target?: number }): Promise<KpiSummary> {
    const url = new URL("/api/analytics/kpi-summary", API_BASE);
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, String(v ?? "")));
    return fetch(url).then(json);
  },

  async revenueTrend(params: CommonParams, _range: RangeKey): Promise<RevenuePoint[]> {
    const url = new URL("/api/analytics/revenue-trend", API_BASE);
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, String(v ?? "")));
    return fetch(url).then(json);
  },

  async topItems(params: CommonParams & { limit?: number }): Promise<TopItem[]> {
    const url = new URL("/api/analytics/top-items", API_BASE);
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, String(v ?? "")));
    return fetch(url).then(json);
  },
};

export type { KpiSummary as TKpiSummary, RevenuePoint as TRevenuePoint, TopItem as TTopItem };
