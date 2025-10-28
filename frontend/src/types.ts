export type KpiSummary = {
  total: number;
  food: number;
  beverage: number;
  target: number;
};

export type RevenuePoint = { date: string; value: number };

export type TopItem = {
  name: string;
  category: "Food" | "Beverage";
  revenue: number;
  qty: number;
};

export type MixDatum = { label: "Food" | "Beverage"; value: number };
