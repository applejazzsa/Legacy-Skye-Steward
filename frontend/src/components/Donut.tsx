// frontend/src/components/Donut.tsx
import React from "react";

type DonutDatum = {
  label: string;
  value: number;
  color?: string; // optional custom color
};

type Props = {
  data: DonutDatum[];
  size?: number;       // overall size in px (square)
  thickness?: number;  // ring thickness
  showCenterTotal?: boolean;
  currencyFormatter?: (n: number) => string; // optional for center label
};

function polarToCartesian(cx: number, cy: number, r: number, angleDeg: number) {
  const angleRad = ((angleDeg - 90) * Math.PI) / 180;
  return { x: cx + r * Math.cos(angleRad), y: cy + r * Math.sin(angleRad) };
}

function arcPath(cx: number, cy: number, r: number, startAngle: number, endAngle: number) {
  const start = polarToCartesian(cx, cy, r, endAngle);
  const end = polarToCartesian(cx, cy, r, startAngle);
  const largeArc = endAngle - startAngle <= 180 ? 0 : 1;
  return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 0 ${end.x} ${end.y}`;
}

const palette = ["#22c55e", "#06b6d4", "#a78bfa", "#f59e0b", "#ef4444"];

export default function Donut({
  data,
  size = 220,
  thickness = 18,
  showCenterTotal = true,
  currencyFormatter,
}: Props) {
  const total = Math.max(0, data.reduce((s, d) => s + Math.max(0, d.value), 0));
  const cx = size / 2;
  const cy = size / 2;
  const rOuter = size / 2 - 2;
  const rInner = rOuter - thickness;
  const ringR = (rOuter + rInner) / 2;

  let angle = 0;
  const segs = data.map((d, i) => {
    const frac = total > 0 ? d.value / total : 0;
    const start = angle;
    const delta = frac * 360;
    const end = start + delta;
    angle = end;

    const color = d.color ?? palette[i % palette.length];
    return { ...d, start, end, color };
  });

  return (
    <div className="donut-wrap" style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: 16 }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} role="img" aria-label="Mix donut">
        {/* background ring */}
        <circle cx={cx} cy={cy} r={ringR} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={thickness} />
        {/* slices */}
        <g>
          {segs.map((s, i) => {
            if (s.end - s.start <= 0) return null;
            const path = arcPath(cx, cy, ringR, s.start, s.end);
            return <path key={i} d={path} stroke={s.color} strokeWidth={thickness} fill="none" strokeLinecap="butt" />;
          })}
        </g>
        {/* center hole */}
        <circle cx={cx} cy={cy} r={rInner} fill="rgba(0,0,0,0.25)" />
        {showCenterTotal && (
          <text
            x={cx}
            y={cy}
            textAnchor="middle"
            dominantBaseline="middle"
            style={{ fill: "rgba(255,255,255,0.9)", fontWeight: 700, fontSize: 14 }}
          >
            {currencyFormatter ? currencyFormatter(total) : total.toLocaleString()}
          </text>
        )}
      </svg>

      {/* legend */}
      <div style={{ alignSelf: "center" }}>
        <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 8 }}>
          {segs.map((s, i) => (
            <li key={i} style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span
                style={{
                  width: 10,
                  height: 10,
                  background: s.color,
                  borderRadius: 2,
                  display: "inline-block",
                }}
              />
              <span style={{ opacity: 0.8 }}>{s.label}</span>
              <span style={{ marginLeft: "auto", fontWeight: 600, opacity: 0.9 }}>
                {currencyFormatter ? currencyFormatter(s.value) : s.value.toLocaleString()}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
