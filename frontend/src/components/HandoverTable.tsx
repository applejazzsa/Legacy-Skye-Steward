import { useEffect, useState } from "react";
import { api, Handover } from "../api";

export default function HandoverTable() {
  const [rows, setRows] = useState<Handover[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    api.handovers()
      .then(setRows)
      .catch(e => setErr(String(e)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="card">
      <h2>Handovers</h2>

      <div style={{display:'flex', gap:8, marginBottom:12}}>
        <button className="button" onClick={api.exportHandoversCsv}>Export CSV</button>
        <button className="button" onClick={api.exportHandoversXlsx}>Export XLSX</button>
      </div>

      {loading && <div className="badge">Loading…</div>}
      {err && <div className="badge" style={{color:'#ef4444'}}>Error: {err}</div>}
      {!loading && !err && (
        <div style={{overflowX: "auto"}}>
          <table className="table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Outlet</th>
                <th>Shift</th>
                <th>Period</th>
                <th>Bookings</th>
                <th>Walk-ins</th>
                <th>Covers</th>
                <th>Food Rev</th>
                <th>Bev Rev</th>
                <th>Top Sales</th>
              </tr>
            </thead>
            <tbody>
              {rows.map(r => (
                <tr key={r.id}>
                  <td>{new Date(r.date).toLocaleString()}</td>
                  <td>{r.outlet}</td>
                  <td>{r.shift}</td>
                  <td>{r.period}</td>
                  <td>{r.bookings}</td>
                  <td>{r.walk_ins}</td>
                  <td>{r.covers}</td>
                  <td>${r.food_revenue.toFixed(2)}</td>
                  <td>${r.beverage_revenue.toFixed(2)}</td>
                  <td>{r.top_sales?.join(", ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
