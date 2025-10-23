import { memo } from "react";

export type RevenuePoint = { d: string; t: number | string | null | undefined };

export default memo(function WeeklyTrends({ data }: { data: RevenuePoint[] }) {
  // 1) Sanitize data: coerce to numbers and remove non-finite points
  const clean = (Array.isArray(data) ? data : [])
    .map((p, i) => ({
      i,
      d: String(p?.d ?? ""),
      t: Number((p as any)?.t ?? 0),
    }))
    .filter((p) => Number.isFinite(p.t));

  if (clean.length === 0) {
    return <p className="muted">No data for selected range.</p>;
  }

  // 2) Dimensions
  const W = 900;
  const H = 220;
  const PAD = 20;

  // 3) Scales (safe against single-point or flat series)
  const xs = clean.map((p) => p.i);
  const ys = clean.map((p) => p.t);

  const minY = Math.min(0, ...ys);
  const maxY = Math.max(1, ...ys);

  const spanX = Math.max(xs.length - 1, 1);
  const spanY = Math.max(maxY - minY, 1);

  const x = (i: number) => PAD + (i / spanX) * (W - PAD * 2);
  const y = (v: number) => H - PAD - ((v - minY) / spanY) * (H - PAD * 2);

  // 4) Path
  const dAttr = clean
    .map((p, idx) => `${idx === 0 ? "M" : "L"} ${x(idx)} ${y(p.t)}`)
    .join(" ");

  return (
    <svg width="100%" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Revenue trend">
      <rect x="0" y="0" width={W} height={H} fill="transparent" />
      {/* baseline at y=0 (only if within range) */}
      {minY <= 0 && 0 <= maxY && (
        <line x1={PAD} y1={y(0)} x2={W - PAD} y2={y(0)} stroke="#1b2340" strokeWidth="1" />
      )}
      {/* line */}
      <path d={dAttr} fill="none" stroke="#58a6ff" strokeWidth="2" />
      {/* points */}
      {clean.map((p, idx) => (
        <circle key={p.i} cx={x(idx)} cy={y(p.t)} r="2.5" fill="#58a6ff" />
      ))}
    </svg>
  );
});
