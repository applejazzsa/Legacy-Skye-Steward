import { useEffect, useState } from "react";
import { api } from "../api";
import { useAppStore, makeRange } from "../store";

type Log = { id: number; when_ts: string; author?: string; text: string; tags?: string };

export default function Concierge() {
  const { tenant, range } = useAppStore();
  const { date_from, date_to } = makeRange(range);
  const [logs, setLogs] = useState<Log[]>([]);
  const [text, setText] = useState("");
  const [author, setAuthor] = useState("");
  const [tags, setTags] = useState("");

  async function refresh() {
    const list = await api.conciergeList({ tenant, date_from, date_to });
    setLogs(Array.isArray(list) ? list : []);
  }
  useEffect(() => { refresh(); }, [tenant, range]);

  return (
    <div className="row two">
      <div className="card">
        <h3>Front-of-House Log</h3>
        <div className="muted">Quick notes for Concierge/FOH activities</div>
        <div style={{ display:'grid', gap:8, marginTop:8 }}>
          <input placeholder="Author (optional)" value={author} onChange={(e)=>setAuthor(e.target.value)} />
          <input placeholder="Tags (comma-separated)" value={tags} onChange={(e)=>setTags(e.target.value)} />
          <textarea rows={3} placeholder="Note" value={text} onChange={(e)=>setText(e.target.value)} />
          <div>
            <button className="primary" onClick={async ()=>{ if (!text.trim()) return; await api.conciergeCreate({ tenant, text: text.trim(), author: author || undefined, tags: tags || undefined }); setText(""); setTags(""); await refresh(); }}>Add</button>
          </div>
        </div>
      </div>
      <div className="card">
        <h3>Recent</h3>
        <table className="table">
          <thead><tr><th>When</th><th>Author</th><th>Tags</th><th>Note</th></tr></thead>
          <tbody>
            {logs.map(l => (
              <tr key={l.id}><td>{new Date(l.when_ts).toLocaleString()}</td><td>{l.author || ''}</td><td>{l.tags || ''}</td><td>{l.text}</td></tr>
            ))}
            {!logs.length && <tr><td className="muted" colSpan={4}>No entries.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}

