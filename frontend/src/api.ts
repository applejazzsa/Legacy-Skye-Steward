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
  avg_check?: number;
  revenue_vs_prev: number;
  target: number;
  target_gap: number;
};

export type TopItem = { item: string; count: number };

export type IncidentStatus = "OPEN" | "IN_PROGRESS" | "CLOSED";
export type IncidentSeverity = "LOW" | "MEDIUM" | "HIGH";

export type IncidentFollowUp = {
  id: number;
  note: string;
  owner?: string;
  due_date?: string;
  done_at?: string;
  created_at: string;
  updated_at: string;
};

export type Incident = {
  id: number;
  title: string;
  description?: string;
  area?: string;
  owner?: string;
  status: IncidentStatus;
  severity: IncidentSeverity;
  due_date?: string;
  resolved_at?: string;
  created_at: string;
  updated_at: string;
  followups: IncidentFollowUp[];
};

export type IncidentCreate = {
  title: string;
  description?: string;
  area?: string;
  owner?: string;
  status?: IncidentStatus;
  severity?: IncidentSeverity;
  due_date?: string;
  first_followup?: { note: string; owner?: string; due_date?: string };
};

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

async function post<T>(path: string, body: any): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

export const api = {
  health: () => get<{ status: string }>("/health"),
  handovers: () => get<Handover[]>("/api/handover"),
  guestNotes: () => get<GuestNote[]>("/api/guest-notes"),
  kpiSummary: (target: number) => get<KpiSummary>(`/api/analytics/kpi-summary?target=${encodeURIComponent(target)}`),
  topItems: (limit = 5) => get<TopItem[]>(`/api/analytics/top-items?limit=${encodeURIComponent(limit)}`),

  incidents: () => get<Incident[]>("/api/incidents"),
  createIncident: (payload: IncidentCreate) => post<Incident>("/api/incidents", payload),

  weekly: (weeks=8) => get<{week:string; revenue:number; covers:number}[]>(`/api/analytics/weekly?weeks=${weeks}`),

  exportHandoversCsv: () => window.open(`${API_BASE}/api/export/handovers.csv`, "_blank"),
  exportHandoversXlsx: () => window.open(`${API_BASE}/api/export/handovers.xlsx`, "_blank"),
  exportIncidentsCsv: () => window.open(`${API_BASE}/api/export/incidents.csv`, "_blank"),
  exportIncidentsXlsx: () => window.open(`${API_BASE}/api/export/incidents.xlsx`, "_blank"),
};
