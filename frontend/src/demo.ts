// frontend/src/demo.ts

import type { RevenuePoint, KpiSummary, TopItem } from "./api";

/** Deterministic pseudo-random (seed by date range) so charts don’t jump every reload */
function seededRand(seed: number) {
  let x = Math.sin(seed) * 10000;
  return () => {
    x = Math.sin(x) * 10000;
    return x - Math.floor(x);
  };
}

function daysBetween(fromISO: string, toISO: string) {
  const a = new Date(fromISO);
  const b = new Date(toISO);
  const ms = Math.max(0, b.getTime() - a.getTime());
  return Math.floor(ms / (24 * 60 * 60 * 1000)) + 1;
}

export function demoTrend(date_from: string, date_to: string): RevenuePoint[] {
  const days = daysBetween(date_from, date_to);
  const start = new Date(date_from);
  const seed = start.getFullYear() * 10000 + (start.getMonth() + 1) * 100 + start.getDate();
  const rnd = seededRand(seed);

  const out: RevenuePoint[] = [];
  let base = 4000 + rnd() * 4000; // base range ~ R4k–R8k daily

  for (let i = 0; i < days; i++) {
    const d = new Date(start);
    d.setDate(d.getDate() + i);

    // add some weekly-ish wave and randomness
    const wave = Math.sin((i / 7) * Math.PI * 2) * 1800;
    const noise = (rnd() - 0.5) * 1200;
    const total = Math.max(500, base + wave + noise);

    out.push({
      d: d.toISOString().slice(0, 10),
      t: Math.round(total),
    });
  }
  return out;
}

export const demoTop: TopItem[] = [
  { name: "Truffle Pasta", category: "Food", qty: 37, revenue: 9250 },
  { name: "Ribeye",        category: "Food", qty: 31, revenue: 11300 },
  { name: "Merlot",        category: "Beverage", qty: 44, revenue: 6600 },
  { name: "Margherita",    category: "Food", qty: 40, revenue: 8400 },
  { name: "IPA",           category: "Beverage", qty: 58, revenue: 8700 },
];

export function demoKpi(trend: RevenuePoint[], target: number): KpiSummary {
  const total = trend.reduce((s, p) => s + p.t, 0);
  // simple split for demo
  const food = Math.round(total * 0.62);
  const beverage = total - food;

  return {
    total,
    food,
    beverage,
    target,
    target_pct: target > 0 ? (total / target) * 100 : 0,
  };
}
