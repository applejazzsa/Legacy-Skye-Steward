import { useEffect, useState } from "react";
import { api, TopItem } from "../api";

export default function TopItems() {
  const [items, setItems] = useState<TopItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    api.topItems(5)
      .then(setItems)
      .catch(e => setErr(String(e)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="card">
      <h2>Top Items</h2>
      {loading && <div className="badge">Loading…</div>}
      {err && <div className="badge" style={{color:'#ef4444'}}>Error: {err}</div>}
      {!loading && !err && (
        <ul style={{listStyle:'none', padding:0, margin:0}}>
          {items.map((x, i) => (
            <li key={`${x.item}-${i}`} style={{display:'flex', justifyContent:'space-between', borderBottom:'1px solid var(--border)', padding:'8px 0'}}>
              <span style={{display:'flex', gap:8}}>
                <span className="badge">#{i+1}</span>
                <strong>{x.item}</strong>
              </span>
              <span className="badge">
                {typeof x.count === "number" ? `${x.count} orders` : `—`}
              </span>
            </li>
          ))}
          {items.length === 0 && <div className="badge">No data.</div>}
        </ul>
      )}
    </div>
  );
}
