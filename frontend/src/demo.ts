import type { KpiSummary, TopItem, RevenuePoint } from "./types";

export const demoTop: TopItem[] = [
  { name: "Ribeye", category: "Food", revenue: 38000, qty: 120 },
  { name: "Merlot", category: "Beverage", revenue: 24000, qty: 160 },
  { name: "Margherita", category: "Food", revenue: 21000, qty: 140 },
  { name: "IPA", category: "Beverage", revenue: 26000, qty: 200 },
];

export function demoTrend(date_from: string, date_to: string): RevenuePoint[] {
  const out: RevenuePoint[] = [];
  const start = new Date(date_from);
  const end = new Date(date_to);
  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    const v = 18000 + Math.round(Math.random() * 12000);
    out.push({ date: d.toISOString().slice(0, 10), value: v });
  }
  return out;
}

export function demoKpi(trend: RevenuePoint[], target: number): KpiSummary {
  const total = trend.reduce((s, p) => s + p.value, 0);
  const food = Math.round(total * 0.58);
  const beverage = total - food;
  return { total, food, beverage, target };
}
