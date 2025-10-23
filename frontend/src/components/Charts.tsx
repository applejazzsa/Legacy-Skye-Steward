import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  CartesianGrid,
} from "recharts";
import { Card, Empty, Skeleton } from "./ui";

const tickColor = "rgba(255,255,255,0.7)";
const gridColor = "rgba(255,255,255,0.08)";
const tooltipStyle = {
  background: "rgba(0,0,0,0.9)",
  border: "1px solid rgba(255,255,255,0.1)",
  borderRadius: "8px",
};

function currency(n: number) {
  return `$${(n ?? 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
}

export function RevenueTrend({
  data,
  loading,
}: {
  data: { date: string; total: number }[] | null;
  loading: boolean;
}) {
  return (
    <Card>
      <div className="mb-3 text-base font-medium text-white/80">Revenue Trend</div>
      {loading ? (
        <Skeleton className="h-56" />
      ) : !data || data.length === 0 ? (
        <Empty title="No revenue in this range." note="Try expanding your date range." />
      ) : (
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
              <XAxis
                dataKey="date"
                stroke={tickColor}
                tickFormatter={(d) => String(d).slice(5)} // show MM-DD
                minTickGap={24}
              />
              <YAxis stroke={tickColor} tickFormatter={(v) => `$${v}`} />
              <Tooltip
                formatter={(v: any) => (typeof v === "number" ? currency(v) : v)}
                contentStyle={tooltipStyle}
                labelStyle={{ color: "white" }}
              />
              <Line type="monotone" dataKey="total" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  );
}

export function MixChart({
  food,
  beverage,
  loading,
}: {
  food: number;
  beverage: number;
  loading: boolean;
}) {
  const data = [
    { name: "Food", value: food },
    { name: "Beverage", value: beverage },
  ];
  const hasAny = (food ?? 0) + (beverage ?? 0) > 0;

  return (
    <Card>
      <div className="mb-3 text-base font-medium text-white/80">Mix (Food vs Beverage)</div>
      {loading ? (
        <Skeleton className="h-56" />
      ) : !hasAny ? (
        <Empty title="No mix to show." />
      ) : (
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "white" }} />
              <Pie data={data} dataKey="value" nameKey="name" innerRadius={55} outerRadius={85}>
                {data.map((_, i) => (
                  <Cell key={i} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  );
}

export function TopItems({
  data,
  loading,
}: {
  data: { name: string; units_sold: number; revenue: number }[] | null;
  loading: boolean;
}) {
  return (
    <Card>
      <div className="mb-3 text-base font-medium text-white/80">Top Items</div>
      {loading ? (
        <Skeleton className="h-60" />
      ) : !data || data.length === 0 ? (
        <Empty title="No items found for this range." />
      ) : (
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 24 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
              <XAxis dataKey="name" tick={{ fill: tickColor }} interval={0} height={36} />
              <YAxis tick={{ fill: tickColor }} tickFormatter={(v) => `$${v}`} />
              <Tooltip
                formatter={(v: any, k: string) =>
                  k === "revenue" && typeof v === "number" ? currency(v) : v
                }
                contentStyle={tooltipStyle}
                labelStyle={{ color: "white" }}
              />
              <Bar dataKey="revenue" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  );
}
