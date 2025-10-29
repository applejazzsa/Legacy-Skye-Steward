import React from "react";

type BarDatum = { label: string; actual: number; target: number };

export default function Bars({ data }: { data: BarDatum[] }) {
  const max = Math.max(1, ...data.map(d => Math.max(d.actual, d.target)));
  const height = 220;
  const barW = 40;
  const gap = 28;
  const width = data.length * (barW * 2 + gap) + gap;
  return (
    <svg width={width} height={height} role="img" aria-label="Department performance bars">
      {data.map((d, i) => {
        const x = gap + i * (barW * 2 + gap);
        const aH = Math.round((d.actual / max) * (height - 40));
        const tH = Math.round((d.target / max) * (height - 40));
        const yA = height - aH - 20;
        const yT = height - tH - 20;
        return (
          <g key={d.label}>
            <rect x={x} y={yT} width={barW} height={tH} fill="#1f3a5f" />
            <rect x={x + barW} y={yA} width={barW} height={aH} fill="#4cc9f0" />
            <text x={x + barW} y={height - 4} fill="#9aa4b2" fontSize={10} textAnchor="middle">{d.label}</text>
          </g>
        );
      })}
    </svg>
  );
}

