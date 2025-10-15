import { useEffect, useState } from "react";
import { api, KpiSummary } from "../api";

export default function KpiSummaryCard() {
  const [target, setTarget] = useState(10000);
  const [data, setData] = useState<KpiSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  const load = (t: number) => {
    setLoading(true);
    setErr(null);
    api.kpiSummary(t)
      .then(setData)
      .catch(e => setErr(String(e)))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(target); }, []);

  const fmtMoney = (v?: number) =>
    typeof v === "number" ? `$${v.toLocaleString(undefined, { maximumFractionDigits: 0 })}` : "—";

  const fmt2 = (v?: number) =>
    typeof v === "number" ? (Number(v).toFixed(2)) : "0.00";

  return (
    <div className="card">
      <h2>KPI Summary</h2>
      <div style={{display:'flex', gap:8, marginBottom:12}}>
        <input
          className="input"
          type="number"
          value={target}
          onChange={e => setTarget(parseInt(e.target.value || "0", 10))}
          placeholder="Target revenue"
        />
        <button className="button" onClick={() => load(target)}>Refresh</button>
      </div>
      {loading && <div className="badge">Loading…</div>}
      {err && <div className="badge" style={{color:'#ef4444'}}>Error: {err}</div>}
      {!loading && !err && data && (
        <>
          <div className="row">
            <div className="kpi">
              <div className="label">Window</div>
              <div className="value">{data.window || "—"}</div>
            </div>
            <div className="kpi">
              <div className="label">Covers</div>
              <div className="value">{Number(data.covers ?? 0).toLocaleString()}</div>
            </div>
            <div className="kpi">
              <div className="label">Revenue</div>
              <div className="value">{fmtMoney(data.revenue)}</div>
            </div>
          </div>

          <div className="row" style={{marginTop:8}}>
            <div className="kpi">
              <div className="label">Avg Check</div>
              <div className="value">${fmt2(data.avg_check)}</div>
            </div>
            <div className="kpi">
              <div className="label">Vs Previous</div>
              <div className={`value ${Number(data.revenue_vs_prev) >= 0 ? 'pos' : 'neg'}`}>
                {Number(data.revenue_vs_prev) >= 0 ? '▲' : '▼'} {fmtMoney(Math.abs(Number(data.revenue_vs_prev)))}
              </div>
            </div>
            <div className="kpi">
              <div className="label">Target Gap</div>
              <div className={`value ${Number(data.target_gap) <= 0 ? 'pos' : 'neg'}`}>
                {Number(data.target_gap) <= 0 ? '✓' : '△'} {fmtMoney(Math.abs(Number(data.target_gap)))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
