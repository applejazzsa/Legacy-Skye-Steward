interface KpiCardProps {
  title: string;
  current: number;
  previous: number;
  change: number;
  format?: "currency" | "number";
}

function formatValue(value: number, format: "currency" | "number" = "number"): string {
  if (format === "currency") {
    return value.toLocaleString(undefined, {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }
  return value.toLocaleString(undefined, {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  });
}

export default function KpiCard({ title, current, previous, change, format = "number" }: KpiCardProps) {
  const changeColor = change > 0 ? "text-emerald-600" : change < 0 ? "text-rose-600" : "text-slate-500";
  const symbol = change > 0 ? "+" : change < 0 ? "" : "";

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-sm font-semibold text-slate-600">{title}</h3>
      <p className="mt-2 text-2xl font-semibold text-slate-900">{formatValue(current, format)}</p>
      <p className="mt-1 text-xs text-slate-500">Prev: {formatValue(previous, format)}</p>
      <p className={`mt-3 text-sm font-medium ${changeColor}`}>
        {symbol}
        {change.toFixed(1)}%
      </p>
    </div>
  );
}
