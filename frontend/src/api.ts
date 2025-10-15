const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";

export type Handover = {
  id: number;
  outlet: string;
  date: string;
  shift: "AM" | "PM";
  period: string;
  bookings: number;
  walk_ins: number;
  covers: number;
  food_revenue: number;
  beverage_revenue: number;
  top_sales: string[];
  created_at: string;
  updated_at: string;
};

export type GuestNote = {
  id: number;
  guest_name: string;
  note: string;
  created_at: string;
};

export type KpiSummary = {
  window: string;
  covers: number;
  revenue: number;
  avg_check: number;
  revenue_vs_prev: number;
  target: number;
  target_gap: number;
};

export type TopItem = { item: string; count: number };

async function get<T = unknown>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

const n = (v: any, fallback = 0): number => {
  const x = typeof v === "string" ? Number(v) : v;
  return Number.isFinite(x) ? (x as number) : fallback;
};

// -------- Normalizers --------
function normalizeTopItems(payload: any): TopItem[] {
  const arr = Array.isArray(payload) ? payload
    : (payload && Array.isArray(payload.items)) ? payload.items
    : [];

  if (!Array.isArray(arr)) return [];

  if (arr.length > 0 && typeof arr[0] === "string") {
    return (arr as string[]).map(s => ({ item: s, count: 0 }));
  }

  return (arr as any[]).map((x) => {
    if (x && typeof x === "object") {
      const item = String(x.item ?? x.name ?? x.label ?? "");
      const countVal = n(x.count ?? x.value, 0);
      return { item, count: countVal };
    }
    return { item: String(x), count: 0 };
  });
}

function normalizeKpiSummary(payload: any): KpiSummary {
  return {
    window: String(payload?.window ?? ""),
    covers: n(payload?.covers, 0),
    revenue: n(payload?.revenue, 0),
    avg_check: n(payload?.avg_check ?? (payload?.revenue && payload?.covers ? payload.revenue / Math.max(1, payload.covers) : undefined), 0),
    revenue_vs_prev: n(payload?.revenue_vs_prev, 0),
    target: n(payload?.target, 0),
    target_gap: n(payload?.target_gap ?? (payload?.target && payload?.revenue ? payload.target - payload.revenue : undefined), 0),
  };
}

// -------- API --------
export const api = {
  health: () => get<{ status: string }>("/health"),
  handovers: () => get<Handover[]>("/api/handover"),
  guestNotes: () => get<GuestNote[]>("/api/guest-notes"),
  kpiSummary: async (target: number): Promise<KpiSummary> => {
    const raw = await get<any>(`/api/analytics/kpi-summary?target=${encodeURIComponent(target)}`);
    return normalizeKpiSummary(raw);
  },
  topItems: async (limit = 5): Promise<TopItem[]> => {
    const raw = await get<any>(`/api/analytics/top-items?limit=${encodeURIComponent(limit)}`);
    return normalizeTopItems(raw);
  },
};
