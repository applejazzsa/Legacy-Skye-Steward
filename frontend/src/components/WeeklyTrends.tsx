import { useEffect, useState } from "react";
import { api } from "../api";

type Point = { week: string; revenue: number; covers: number };

export default function WeeklyTrends() {
  const [data, setData] = useState<Point[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    api
      .weekly(8)
      .then(setData)
      .catch((e) => setErr(String(e)))
      .finally(() => setLoading(false));
  }, []);

  const w = 520,
    h = 120,
    pad = 20;
  const maxRev = Math.max(1, ...data.map((d) => d.revenue));
  const x = (i: number) =>
    pad + (i * (w - 2 * pad)) / Math.max(1, data.length - 1);
  const y = (v: number) => h - pad - (v / maxRev) * (h - 2 * pad);
  const path = data
    .map((d, i) => `${i === 0 ? "M" : "L"} ${x(i)} ${y(d.revenue)}`)
    .join(" ");

  return (
    <div className="card">
      <h2>Weekly Trends (Revenue)</h2>
      {loading && <div className="badge">Loading…</div>}
      {err && <div className="badge" style={{ color: "#ef4444" }}>Error: {err}</div>}
      {!loading && !err && data.length > 0 && (
        <>
          <svg width={w} height={h} role="img" aria-label="Weekly revenue trend">
            <path d={path} fill="none" stroke="white" strokeWidth="2" />
            {data.map((d, i) => (
              <circle key={d.week} cx={x(i)} cy={y(d.revenue)} r={2.5} />
            ))}
          </svg>
          <div className="sub" style={{ marginTop: 6 }}>
            {data.map((d) => d.week).join("  ·  ")}
          </div>
        </>
      )}
      {!loading && !err && data.length === 0 && (
        <div className="badge">No trend data.</div>
      )}
    </div>
  );
}
