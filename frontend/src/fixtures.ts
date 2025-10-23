import { KpiSummary, RevenuePoint, TopItem, MixDatum } from "./types";
import { rangeFromKey } from "./utils/date";

export const fixtureKpi: KpiSummary = {
  total: 0,
  food: 0,
  beverage: 0,
  target: 10000,
  pctToTarget: 0,
};

export function fixtureTrend(key: "7d" | "14d" | "30d"): RevenuePoint[] {
  const { date_from } = rangeFromKey(key);
  const start = new Date(date_from);
  const n = key === "7d" ? 7 : key === "14d" ? 14 : 30;
  const out: RevenuePoint[] = [];
  for (let i = 0; i < n; i++) {
    const d = new Date(start);
    d.setDate(start.getDate() + i);
    out.push({ date: d.toISOString().slice(0, 10), total: 0 });
  }
  return out;
}

export const fixtureMix: MixDatum[] = [
  { label: "Food", value: 0 },
  { label: "Beverage", value: 0 },
];

export const fixtureTopItems: TopItem[] = [
  { name: "Truffle Pasta", revenue: 120, qty: 12, category: "Food" },
  { name: "Ribeye", revenue: 95, qty: 7, category: "Food" },
  { name: "Merlot", revenue: 58, qty: 11, category: "Beverage" },
  { name: "Margherita", revenue: 93, qty: 10, category: "Food" },
  { name: "IPA", revenue: 121, qty: 24, category: "Beverage" },
];
