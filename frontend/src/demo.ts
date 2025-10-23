import type { RevenuePoint, TopItem, KpiSummary } from "./types";

export const demoTrend = (fromISO: string, toISO: string): RevenuePoint[] => {
  const from = new Date(fromISO);
  const to = new Date(toISO);
  const out: RevenuePoint[] = [];
  const msDay = 24 * 60 * 60 * 1000;
  for (let t = from.getTime(); t <= to.getTime(); t += msDay) {
    const d = new Date(t);
    // gentle seasonality + noise
    const base = 6500 + 1500 * Math.sin(t / (5 * msDay));
    const noise = Math.floor(Math.random() * 600);
    out.push({ date: d.toISOString().slice(0,10), total: Math.max(1200, Math.round(base + noise)) });
  }
  return out;
};

export const demoTop: TopItem[] = [
  { name: "Truffle Pasta", category: "Food", qty: 124, revenue: 18600 },
  { name: "Ribeye",        category: "Food", qty:  91, revenue: 22750 },
  { name: "Merlot",        category: "Beverage", qty: 73, revenue: 10950 },
  { name: "Margherita",    category: "Food", qty: 102, revenue: 15300 },
  { name: "IPA",           category: "Beverage", qty: 88, revenue: 13200 },
];

export const demoKpi = (trend: RevenuePoint[], target = 10000): KpiSummary => {
  const total = trend.reduce((s, d) => s + d.total, 0);
  const food = Math.round(total * 0.62);
  const beverage = total - food;
  return {
    total,
    food,
    beverage,
    target,
    percent_of_target: target ? Math.round((total / target) * 100) : 0,
  };
};
