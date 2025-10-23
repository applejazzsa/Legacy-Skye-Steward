const API_BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

type Q = Record<string, string | number | undefined | null>;

function toQuery(params: Q) {
  const usp = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") usp.set(k, String(v));
  });
  return usp.toString();
}

async function get<T>(path: string, params?: Q): Promise<T> {
  const url = `${API_BASE}${path}${params ? `?${toQuery(params)}` : ""}`;
  const res = await fetch(url);
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText} — ${text}`);
  }
  return res.json();
}

export const AnalyticsAPI = {
  kpiSummary: (date_from?: string, date_to?: string, target?: number) =>
    get<KPISummary>("/api/analytics/kpi-summary", { date_from, date_to, target }),
  revenueTrend: (date_from?: string, date_to?: string) =>
    get<RevenuePoint[]>("/api/analytics/revenue-trend", { date_from, date_to }),
  topItems: (limit = 5, date_from?: string, date_to?: string) =>
    get<TopItem[]>("/api/analytics/top-items", { limit, date_from, date_to }),
};
