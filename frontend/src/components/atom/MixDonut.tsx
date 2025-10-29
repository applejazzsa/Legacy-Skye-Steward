import type { MixDatum } from "../../types";
import { formatZAR } from "../../util/currency";

type Props = { data: MixDatum[] };

export default function MixDonut({ data }: Props) {
  const safe = (v: unknown) => (Number.isFinite(Number(v)) ? Number(v) : 0);
  const list = Array.isArray(data) ? data : [];
  const vals = list.map((d) => safe(d.value));
  const total = vals.reduce((s, v) => s + v, 0);

  const radius = 85;
  const circ = 2 * Math.PI * radius;

  let acc = 0;
  const segments = vals.map((v, i) => {
    const frac = total > 0 ? v / total : 0;
    const len = circ * Math.max(0, Math.min(1, frac));
    const dash = `${len} ${Math.max(0, circ - len)}`;
    const stroke = i === 0 ? "#4cc9f0" : "#7c3aed";
    const rotate = (acc / circ) * 360;
    acc += len;
    return (
      <circle
        key={i}
        cx={110}
        cy={110}
        r={radius}
        fill="transparent"
        stroke={stroke}
        strokeWidth={18}
        strokeDasharray={dash}
        transform={`rotate(-90 110 110) rotate(${rotate} 110 110)`}
        strokeLinecap="butt"
      />
    );
  });

  return (
    <div style={{ textAlign: "center" }} aria-label="Food vs Beverage donut chart">
      <svg className="svg-donut" viewBox="0 0 220 220">
        <circle cx={110} cy={110} r={radius} fill="transparent" stroke="#1f2a44" strokeWidth={18} />
        {segments}
        <text x={110} y={110} textAnchor="middle" dominantBaseline="middle" fontSize={14} fill="#9aa4b2">
          {formatZAR(total)}
        </text>
      </svg>
      <div style={{ display: "flex", justifyContent: "center", gap: 12 }}>
        {list.map((d, i) => (
          <div key={d.label ?? i} style={{ display: "flex", gap: 6, alignItems: "center" }}>
            <span style={{ width: 10, height: 10, borderRadius: 3, background: i === 0 ? "#4cc9f0" : "#7c3aed" }} />
            <span style={{ fontSize: 12, color: "#9aa4b2" }}>
              {`${d.label ?? `Segment ${i + 1}`} - ${formatZAR(safe(d.value))}`}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

