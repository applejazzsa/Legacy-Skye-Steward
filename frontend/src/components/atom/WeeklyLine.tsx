import type { RevenuePoint } from "../../types";
import { formatZAR } from "../../util/currency";

type Props = {
  data: Array<RevenuePoint | { date: string; total: number }>;
  events?: Array<{ at: string; label: string }>;
};

export default function WeeklyLine({ data, events }: Props) {
  const clean: RevenuePoint[] = (data ?? []).map((d, i) => {
    const raw = (d as any).value ?? (d as any).total ?? 0;
    const v = Number.isFinite(+raw) ? +raw : 0;
    return { date: (d as any).date || String(i), value: v } as RevenuePoint;
  });

  if (!clean.length) return <p className="muted">No data.</p>;

  const w = 760;
  const h = 220;
  const pad = 18;

  const ys = clean.map((d) => (Number.isFinite(+d.value) ? +d.value : 0));
  const min = Math.min(...ys);
  const max = Math.max(...ys);

  // Avoid zero division and NaN. For 1 point or flat series, draw a flat line.
  const count = clean.length;
  const denom = Math.max(count - 1, 1);
  const range = Math.max(max - min, 1);

  const x = (i: number) => pad + (i * (w - pad * 2)) / denom;
  const y = (v: number) => h - pad - ((v - min) * (h - pad * 2)) / range;

  const path = clean
    .map((d, i) => `${i ? "L" : "M"} ${x(i)} ${y(d.value)}`)
    .join(" ");

  const points = clean.map((d, i) => (
    <circle key={i} cx={x(i)} cy={y(d.value)} r={2.7} fill="#4cc9f0">
      <title>{`${d.date} - ${formatZAR(d.value)}`}</title>
    </circle>
  ));

  // Event badges + labels with very light collision avoidance
  const labelSlots: Array<{ x: number; y: number }> = [];
  const badges = (events || []).map((e, idx) => {
    const d = clean.findIndex((p) => String(p.date) === (e.at || "").slice(0, 10));
    if (d < 0) return null;
    const cx = x(d);
    let cy = y(clean[d].value) - 10;
    // nudge vertically if another label is too close horizontally
    for (const s of labelSlots) {
      if (Math.abs(s.x - cx) < 40 && Math.abs(s.y - cy) < 14) {
        cy -= 14; // stack upward
      }
    }
    labelSlots.push({ x: cx, y: cy });
    return (
      <g key={`ev-${idx}`}>
        <circle cx={cx} cy={cy} r={4.5} fill="#f59e0b">
          <title>{e.label}</title>
        </circle>
        <text x={cx + 6} y={cy + 4} fontSize={10} fill="#f59e0b" aria-hidden="true">
          {e.label}
        </text>
      </g>
    );
  });

  return (
    <svg
      className="svg-line"
      viewBox={`0 0 ${w} ${h}`}
      aria-label="Revenue trend line chart"
    >
      <rect x={0} y={0} width={w} height={h} fill="transparent" />
      <path d={path} stroke="#4cc9f0" fill="none" strokeWidth={2} />
      {points}
      {badges}
    </svg>
  );
}
