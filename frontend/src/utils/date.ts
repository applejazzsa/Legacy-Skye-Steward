export function todayISO(): string {
  return new Date().toISOString().slice(0, 10);
}

export function offsetDaysISO(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

export function rangeFromKey(key: "7d" | "14d" | "30d") {
  const date_to = todayISO();
  const map = { "7d": -6, "14d": -13, "30d": -29 } as const;
  const date_from = offsetDaysISO(map[key]);
  return { date_from, date_to };
}
