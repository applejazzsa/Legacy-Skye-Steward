export type KpiSummary = {
  revenue: number;
  avg_check: number;
  tickets: number;
  target?: number;
  target_progress?: number; // 0..1
};

export type RevenuePoint = { x: string; y: number };

export type TopItem = {
  name: string;
  qty: number;
  revenue: number;
  category: "Food" | "Beverage" | string;
};

export type MixDatum = { label: string; value: number };

export type DateRange = {
  date_from: string; // YYYY-MM-DD
  date_to: string;   // YYYY-MM-DD
};
