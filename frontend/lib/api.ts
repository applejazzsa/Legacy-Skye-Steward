export interface KPISummary {
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
  change_pct: {
    covers: number;
    total_revenue: number;
    avg_check: number;
  };
  target: {
    total_revenue_target: number;
    achievement_pct: number;
  };
}

export interface TopItem {
  item: string;
  count: number;
}

export interface StaffPraise {
  staff: string;
  count: number;
}

export interface Handover {
  id: number;
  outlet: string;
  date: string;
  shift: string;
  period: string | null;
  bookings: number;
  walk_ins: number;
  covers: number;
  food_revenue: number;
  beverage_revenue: number;
  top_sales: string[];
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    cache: "no-store",
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

export async function fetchKpiSummary(target: number): Promise<KPISummary> {
  const query = new URLSearchParams({ target: target.toString() });
  return fetchJson<KPISummary>(`/api/analytics/kpi-summary?${query.toString()}`);
}

export async function fetchTopItems(limit: number): Promise<TopItem[]> {
  const query = new URLSearchParams({ limit: limit.toString() });
  return fetchJson<TopItem[]>(`/api/analytics/top-items?${query.toString()}`);
}

export async function fetchStaffPraise(limit: number): Promise<StaffPraise[]> {
  const query = new URLSearchParams({ limit: limit.toString() });
  return fetchJson<StaffPraise[]>(`/api/analytics/staff-praise?${query.toString()}`);
}

export async function fetchHandovers(limit: number): Promise<Handover[]> {
  const handovers = await fetchJson<Handover[]>(`/api/handover`);
  return handovers.slice(0, limit);
}
