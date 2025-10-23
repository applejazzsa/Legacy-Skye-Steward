// src/lib/format.ts
export const money = (n: number) =>
  new Intl.NumberFormat("en-ZA", { style: "currency", currency: "ZAR", maximumFractionDigits: 0 }).format(
    isFinite(n) ? n : 0
  );

export const pct = (n: number) =>
  `${Math.round((isFinite(n) ? n : 0) * 100)}%`;
