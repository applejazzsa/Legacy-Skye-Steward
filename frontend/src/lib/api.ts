const API_BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

async function get<T>(path: string, signal?: AbortSignal): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { signal, headers: { Accept: "application/json" } });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText} – ${text}`);
  }
  return res.json();
}

export type KpiSummary = { covers: number; revenue: number };
export type TopItem = { name: string; count: number };
export type Handover = {
  id: number; outlet: string; date: string; shift: string; period: string;
  bookings: number; walk_ins: number; covers: number;
  food_revenue: number; beverage_revenue: number; top_sales: string;
};
export type GuestNote = { id: number; guest_name: string; note: string; created_at: string };
export type Incident = {
  id: number; title: string; description: string; area: string; owner: string;
  status: string; severity: string; due_date: string | null; resolved_at: string | null;
  created_at: string; updated_at: string;
};

export const api = {
  kpiSummary: (target = 10000, signal?: AbortSignal) =>
    get<KpiSummary>(`/api/analytics/kpi-summary?target=${encodeURIComponent(target)}`, signal),

  topItems: (limit = 5, signal?: AbortSignal) =>
    get<TopItem[]>(`/api/analytics/top-items?limit=${encodeURIComponent(limit)}`, signal),

  handovers: (signal?: AbortSignal) => get<Handover[]>(`/api/handover`, signal),

  guestNotes: (signal?: AbortSignal) => get<GuestNote[]>(`/api/guest-notes`, signal),

  incidents: (signal?: AbortSignal) => get<Incident[]>(`/api/incidents`, signal),
};
