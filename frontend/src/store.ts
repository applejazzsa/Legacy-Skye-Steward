import { useState, useEffect } from "react";

export type Range = "7d" | "14d" | "30d";

export function makeRange(r: Range) {
  const end = new Date();
  const start = new Date();
  const days = r === "7d" ? 6 : r === "14d" ? 13 : 29;
  start.setDate(end.getDate() - days);
  const date_to = end.toISOString().slice(0, 10);
  const date_from = start.toISOString().slice(0, 10);
  return { date_from, date_to };
}

export function useAppStore() {
  const [tenant, setTenant] = useState("legacy");
  const [range, setRange] = useState<Range>("7d");
  const [refreshSec, setRefresh] = useState(30);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setTick((x) => x + 1), refreshSec * 1000);
    return () => clearInterval(t);
  }, [refreshSec]);

  return { tenant, setTenant, range, setRange, refreshSec, setRefresh, tick };
}
