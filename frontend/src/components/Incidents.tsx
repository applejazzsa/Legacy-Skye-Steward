import { useEffect, useState } from "react";
import { api, Incident, IncidentCreate } from "../api";

export default function Incidents() {
  const [list, setList] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  const [form, setForm] = useState<IncidentCreate>({
    title: "",
    area: "",
    owner: "",
    severity: "MEDIUM",
    status: "OPEN",
  });

  const load = () => {
    setLoading(true);
    api.incidents()
      .then(setList)
      .catch(e => setErr(String(e)))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const submit = async () => {
    try {
      if (!form.title.trim()) return;
      await api.createIncident(form);
      setForm({ title: "", area: "", owner: "", severity: "MEDIUM", status: "OPEN" });
      load();
    } catch (e:any) {
      alert(String(e));
    }
  };

  return (
    <div className="card">
      <h2>Incidents & Follow-ups</h2>

      <div style={{display:'grid', gap:8, marginBottom:12}}>
        <input className="input" placeholder="Title" value={form.title} onChange={e=>setForm({...form, title:e.target.value})} />
        <input className="input" placeholder="Area (Restaurant, Spa...)" value={form.area||""} onChange={e=>setForm({...form, area:e.target.value})} />
        <input className="input" placeholder="Owner (optional)" value={form.owner||""} onChange={e=>setForm({...form, owner:e.target.value})} />
        <div style={{display:'flex', gap:8}}>
          <select className="input" value={form.severity} onChange={e=>setForm({...form, severity: e.target.value as any})}>
            <option value="LOW">LOW</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="HIGH">HIGH</option>
          </select>
          <select className="input" value={form.status} onChange={e=>setForm({...form, status: e.target.value as any})}>
            <option value="OPEN">OPEN</option>
            <option value="IN_PROGRESS">IN PROGRESS</option>
            <option value="CLOSED">CLOSED</option>
          </select>
          <button className="button" onClick={submit}>Add</button>
        </div>
      </div>

      <div style={{display:'flex', gap:8, marginBottom:12}}>
        <button className="button" onClick={api.exportIncidentsCsv}>Export CSV</button>
        <button className="button" onClick={api.exportIncidentsXlsx}>Export XLSX</button>
      </div>

      {loading && <div className="badge">Loading…</div>}
      {err && <div className="badge" style={{color:'#ef4444'}}>Error: {err}</div>}
      {!loading && !err && (
        <ul style={{listStyle:'none', padding:0, margin:0}}>
          {list.map(i => (
            <li key={i.id} style={{borderBottom:'1px solid var(--border)', padding:'8px 0'}}>
              <div style={{display:'flex', justifyContent:'space-between', gap:8}}>
                <div>
                  <strong>{i.title}</strong>
                  <div className="sub">{i.area || "—"}</div>
                </div>
                <span className="badge">{i.severity} · {i.status}</span>
              </div>
              {i.description && <div style={{color:'var(--muted)', marginTop:4}}>{i.description}</div>}
              {i.followups?.length > 0 && (
                <div style={{marginTop:6}}>
                  <div className="sub">Follow-ups</div>
                  <ul style={{margin:0, paddingLeft:16}}>
                    {i.followups.map(f => (
                      <li key={f.id} className="sub">{f.note} {f.owner ? `· ${f.owner}` : ""}</li>
                    ))}
                  </ul>
                </div>
              )}
            </li>
          ))}
          {list.length === 0 && <div className="badge">No incidents yet.</div>}
        </ul>
      )}
    </div>
  );
}
