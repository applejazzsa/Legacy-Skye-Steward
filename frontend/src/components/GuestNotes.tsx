import { useEffect, useState } from "react";
import { api, GuestNote } from "../api";

export default function GuestNotes() {
  const [notes, setNotes] = useState<GuestNote[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    api.guestNotes()
      .then(setNotes)
      .catch(e => setErr(String(e)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="card">
      <h2>Guest Notes</h2>
      {loading && <div className="badge">Loading…</div>}
      {err && <div className="badge" style={{color:'#ef4444'}}>Error: {err}</div>}
      {!loading && !err && (
        <ul style={{listStyle:'none', padding:0, margin:0}}>
          {notes.map(n => (
            <li key={n.id} style={{borderBottom:'1px solid var(--border)', padding:'8px 0'}}>
              <div style={{display:'flex', justifyContent:'space-between', gap:8}}>
                <strong>{n.guest_name}</strong>
                <span className="badge">{new Date(n.created_at).toLocaleString()}</span>
              </div>
              <div style={{color:'var(--muted)'}}>{n.note}</div>
            </li>
          ))}
          {notes.length === 0 && <div className="badge">No notes yet.</div>}
        </ul>
      )}
    </div>
  );
}
