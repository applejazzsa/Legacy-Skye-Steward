import { useEffect, useState } from "react";
import { useAppStore } from "../store";
import { makeRange, api } from "../api";

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
    text: "Guest notes API not found. Showing placeholder data.",
    room: "—",
  },
];

export default function GuestNotes() {
  const { tenant, range } = useAppStore();
  const { date_from, date_to } = makeRange(range);
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);

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

  if (loading) return <p className="muted">Loading guest notes…</p>;
  if (notes.length === 0) return <p className="muted">No guest notes.</p>;

  return (
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
  );
}
