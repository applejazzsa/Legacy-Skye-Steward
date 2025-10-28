import { useEffect, useState } from "react";
import { useAppStore, makeRange } from "../store";
import { api } from "../api";

type Note = {
  id: string | number;
  when: string;     // ISO
  author: string;
  text: string;
  room?: string;
};

const MOCK: Note[] = [
  {
    id: "g1",
    when: new Date().toISOString(),
    author: "System",
    text: "Guest notes API not available. Showing placeholder data.",
    room: "",
  },
];

export default function GuestNotes() {
  const { tenant, range } = useAppStore();
  const { date_from, date_to } = makeRange(range);
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState<{ author: string; text: string; room: string }>({ author: "", text: "", room: "" });

  useEffect(() => {
    let alive = true;
    (async () => {
      setLoading(true);
      try {
        const fn: any = (api as any).guestNotes;
        if (typeof fn === "function") {
          const data: Note[] = await fn({ tenant, date_from, date_to });
          if (!alive) return;
          setNotes(Array.isArray(data) ? data : []);
        } else {
          if (!alive) return;
          setNotes(MOCK);
        }
      } catch {
        if (!alive) return;
        setNotes(MOCK);
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, [tenant, range, date_from, date_to]);

  if (loading) return <p className="muted">Loading guest notes...</p>;

  return (
    <div style={{ display: "grid", gap: 12 }}>
      <div className="card" style={{ padding: 12 }}>
        <h3>Add Guest Note</h3>
        <div className="form-grid">
          <div className="field">
            <label htmlFor="note-author">Author</label>
            <input id="note-author" aria-label="Author" value={form.author} onChange={(e)=>setForm(f=>({ ...f, author: e.target.value }))} placeholder="Your name" />
          </div>
          <div className="field">
            <label htmlFor="note-room">Room</label>
            <input id="note-room" aria-label="Room" value={form.room} onChange={(e)=>setForm(f=>({ ...f, room: e.target.value }))} placeholder="Room (optional)" />
          </div>
          <div className="field" style={{ gridColumn: "1 / -1" }}>
            <label htmlFor="note-text">Note</label>
            <textarea id="note-text" aria-label="Note text" rows={3} value={form.text} onChange={(e)=>setForm(f=>({ ...f, text: e.target.value }))} placeholder="Guest preferences, compliments, issues..." />
          </div>
        </div>
        <div style={{ marginTop: 10 }}>
          <button className="primary" disabled={creating || !form.text} onClick={async ()=>{
            setCreating(true);
            await api.createGuestNote({ author: form.author || undefined, text: form.text.trim(), room: form.room || undefined });
            const fn: any = (api as any).guestNotes;
            if (typeof fn === "function") {
              const data: Note[] = await fn({ tenant, date_from, date_to });
              setNotes(Array.isArray(data) ? data : []);
            }
            setCreating(false);
            setForm({ author: "", text: "", room: "" });
          }} aria-label="Add guest note">{creating ? "Saving..." : "Add Note"}</button>
        </div>
      </div>

      {notes.length === 0 && <p className="muted">No guest notes.</p>}

      <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: 8 }}>
        {notes.map((n) => (
          <li key={n.id} className="card" style={{ padding: 10 }}>
            <div style={{ display: "flex", gap: 8, justifyContent: "space-between" }}>
              <strong>{n.author}</strong>
              <span className="muted">{new Date(n.when).toLocaleString()}</span>
            </div>
            <div style={{ marginTop: 6 }}>{n.text}</div>
            {n.room && <div className="muted" style={{ marginTop: 6 }}>Room: {n.room}</div>}
          </li>
        ))}
      </ul>
    </div>
  );
}
