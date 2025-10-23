// frontend/src/api.ts
import type { KpiSummary, RevenuePoint, TopItem } from "./types";

/**
 * Base URL for the FastAPI backend.
 * You can override with: VITE_API_BASE="http://127.0.0.1:8000/api"
 */
export const API_BASE =
  (import.meta as any).env?.VITE_API_BASE ?? "http://127.0.0.1:8000/api";

/** Simple JSON fetch helper with query params support */
async function getJSON<T>(path: string, params?: Record<string, any>): Promise<T> {
  const url = new URL(path, API_BASE);
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v === undefined || v === null) return;
      url.searchParams.set(k, String(v));
    });
  }
  const res = await fetch(url.toString(), { method: "GET" });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`GET ${url.pathname} ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

/** Date-range helper used around the app */
export function makeRange(
  range: "7d" | "14d" | "30d"
): { date_from: string; date_to: string } {
  const today = new Date();
  const to = new Date(Date.UTC(today.getFullYear(), today.getMonth(), today.getDate()));
  const days = range === "30d" ? 30 : range === "14d" ? 14 : 7;
  const from = new Date(to);
  from.setUTCDate(to.getUTCDate() - (days - 1));
  const iso = (d: Date) => d.toISOString().slice(0, 10);
  return { date_from: iso(from), date_to: iso(to) };
}

/** ---------- API surface ---------- */
export const api = {
  kpiSummary: ({
    tenant,
    date_from,
    date_to,
    target,
  }: {
    tenant: string;
    date_from: string;
    date_to: string;
    target?: number;
  }) =>
    getJSON<KpiSummary>("/analytics/kpi-summary", {
      tenant,
      date_from,
      date_to,
      target,
    }),

  revenueTrend: (
    {
      tenant,
      date_from,
      date_to,
    }: {
      tenant: string;
      date_from: string;
      date_to: string;
    },
    _range?: "7d" | "14d" | "30d"
  ) =>
    getJSON<RevenuePoint[]>("/analytics/revenue-trend", {
      tenant,
      date_from,
      date_to,
    }),

  topItems: ({
    tenant,
    date_from,
    date_to,
    limit = 5,
  }: {
    tenant: string;
    date_from: string;
    date_to: string;
    limit?: number;
  }) =>
    getJSON<TopItem[]>("/analytics/top-items", {
      tenant,
      date_from,
      date_to,
      limit,
    }),
};

/** ---------- Fallback helpers (requested) ---------- */
export const isZeroKpi = (k?: any) =>
  !k || [k.total, k.food, k.beverage].every((v) => !v || v === 0);

export const isEmpty = (arr?: any[]) => !arr || arr.length === 0;
