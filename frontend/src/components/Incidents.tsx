import { useEffect, useMemo, useState } from "react";
import { useAppStore, makeRange } from "../store";
import { api } from "../api";
import { useAuth } from "../auth";
import Select from "../atom/Select";

type Incident = {
  id: string | number;
  when: string;     // ISO
  severity: "low" | "medium" | "high" | string;
  summary: string;
  status?: string;
  reported_by?: string;
};

const MOCK: Incident[] = [
  {
    id: "i1",
    when: new Date().toISOString(),
    severity: "low",
    summary: "Incidents API not found. Showing placeholder incident.",
    reported_by: "System",
  },
];

export default function Incidents() {
  const { tenant, range } = useAppStore();
  const { user } = useAuth();
  const { date_from, date_to } = makeRange(range);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [newAction, setNewAction] = useState<{ [id: string]: { title: string; owner: string; due: string } }>({});
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState<{ outlet: string; title: string; severity: string }>({ outlet: "", title: "", severity: "low" });
  const [view, setView] = useState<'open' | 'in_progress' | 'closed' | 'all'>('open');
  const role = useMemo(() => {
    const links = (user?.tenants as any[]) || [];
    const match = links.find((t) => t.slug === tenant || String(t.id) === tenant || t.name === tenant);
    return (match?.role as string | undefined) || undefined;
  }, [user, tenant]);

  useEffect(() => {
    let alive = true;
    (async () => {
      setLoading(true);
      try {
        const status = view === 'all' ? undefined : (view === 'closed' ? ['CLOSED'] : (view === 'in_progress' ? ['IN_PROGRESS'] : ['OPEN','IN_PROGRESS']));
        const data: Incident[] = (await api.incidents({ tenant, status }) as any) || [];
        if (!alive) return;
        setIncidents(Array.isArray(data) ? data : []);
      } catch {
        if (!alive) return;
        setIncidents(MOCK);
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => { alive = false; };
  }, [tenant, range, date_from, date_to, view]);

  async function addAction(incidentId: string | number) {
    const draft = newAction[String(incidentId)] || { title: "", owner: "", due: "" };
    if (!draft.title) return;
    await api.createAction({ incident_id: Number(incidentId), title: draft.title, owner: draft.owner || undefined, due_date: draft.due || undefined });
    setNewAction(prev => ({ ...prev, [String(incidentId)]: { title: "", owner: "", due: "" } }));
  }

  async function createIncident() {
    if (!form.outlet || !form.title) return;
    setCreating(true);
    await api.createIncident({ tenant, outlet: form.outlet.trim(), title: form.title.trim(), severity: form.severity });
    const data: Incident[] = (await api.incidents({ tenant }) as any) || [];
    setIncidents(Array.isArray(data) ? data : []);
    setCreating(false);
    setForm({ outlet: "", title: "", severity: "low" });
  }

  return (
    <div style={{ display: "grid", gap: 12 }}>
      <div className="card" style={{ padding: 12 }}>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', gap: 8, flexWrap:'wrap' }}>
          <h3>Create Incident</h3>
          <div style={{ display:'flex', alignItems:'center', gap: 8 }}>
            <label style={{ color:'var(--muted)', fontSize:12, textTransform:'uppercase', letterSpacing:'.04em' }}>View</label>
            <Select
              id="incidents-view"
              options={[
                { label:'Open', value:'open' as const },
                { label:'In Progress', value:'in_progress' as const },
                { label:'Closed', value:'closed' as const },
                { label:'All', value:'all' as const },
              ]}
              value={view}
              onChange={(v)=>setView(v as any)}
            />
          </div>
        </div>
        <div className="form-grid">
          <div className="field">
            <label htmlFor="incident-outlet">Outlet</label>
            <input id="incident-outlet" aria-label="Outlet" placeholder="e.g., Azure Restaurant" value={form.outlet} onChange={(e)=>setForm(f=>({ ...f, outlet: e.target.value }))} />
          </div>
          <div className="field">
            <label htmlFor="incident-title">Title</label>
            <input id="incident-title" aria-label="Title" placeholder="Incident summary" value={form.title} onChange={(e)=>setForm(f=>({ ...f, title: e.target.value }))} />
          </div>
          <div className="field">
            <label htmlFor="incident-sev">Severity</label>
            <Select
              id="incident-sev"
              options={[
                { label: "LOW", value: "low" as const },
                { label: "MEDIUM", value: "medium" as const },
                { label: "HIGH", value: "high" as const },
              ]}
              value={form.severity as "low" | "medium" | "high"}
              onChange={(v)=>setForm(f=>({ ...f, severity: v }))}
            />
          </div>
        </div>
        <div style={{ marginTop: 10 }}>
          <button className="primary" onClick={createIncident} disabled={creating} aria-label="Create incident">{creating ? "Saving..." : "Add Incident"}</button>
        </div>
      </div>

      {loading && <p className="muted">Loading incidents...</p>}
      {!loading && incidents.length === 0 && <p className="muted">No incidents.</p>}

      {!loading && incidents.length > 0 && (
        <div style={{ display: "grid", gap: 8 }}>
          {incidents.map((i) => (
            <div key={i.id} className="card" style={{ padding: 10 }}>
              <div style={{ display: "flex", gap: 8, justifyContent: "space-between" }}>
                <strong style={{ textTransform: "capitalize" }}>{i.severity}</strong>
                <span className="muted">{new Date(i.when).toLocaleString()}</span>
              </div>
              <div style={{ marginTop: 6 }}>{i.summary}</div>
              <div className="muted" style={{ marginTop: 6 }}>Status: {i.status || "OPEN"}</div>
              {(role === 'manager' || role === 'owner') && (
                <div style={{ marginTop: 8, display: 'flex', gap: 8, alignItems: 'center', flexWrap:'wrap' }}>
                  <label style={{ color: 'var(--muted)', fontSize: 12, textTransform:'uppercase', letterSpacing: '.04em' }}>Update Status</label>
                  <Select
                    id={`incident-status-${i.id}`}
                    options={[{label:'OPEN', value:'OPEN' as const},{label:'IN_PROGRESS', value:'IN_PROGRESS' as const},{label:'CLOSED', value:'CLOSED' as const}]}
                    value={(i.status as 'OPEN'|'IN_PROGRESS'|'CLOSED') || 'OPEN'}
                    onChange={async (v)=>{
                      await api.updateIncident({ tenant, id: Number(i.id), status: String(v) });
                      const data: any = await api.incidents({ tenant });
                      setIncidents(Array.isArray(data) ? data : []);
                    }}
                  />
                </div>
              )}
              {i.reported_by && (
                <div className="muted" style={{ marginTop: 6 }}>
                  Reported by: {i.reported_by}
                </div>
              )}
              <div style={{ display: "flex", gap: 6, marginTop: 8, flexWrap: "wrap" }}>
                <input style={{minWidth:220}} placeholder="Add action." value={(newAction[String(i.id)]?.title)||""} onChange={e=>setNewAction(prev=>({ ...prev, [String(i.id)]: { ...(prev[String(i.id)]||{owner:"", due:""}), title: e.target.value } }))} />
                <input placeholder="Owner (optional)" value={(newAction[String(i.id)]?.owner)||""} onChange={e=>setNewAction(prev=>({ ...prev, [String(i.id)]: { ...(prev[String(i.id)]||{title:"", due:""}), owner: e.target.value } }))} />
                <input type="date" placeholder="Due" value={(newAction[String(i.id)]?.due)||""} onChange={e=>setNewAction(prev=>({ ...prev, [String(i.id)]: { ...(prev[String(i.id)]||{title:"", owner:""}), due: e.target.value } }))} />
                <button onClick={()=>addAction(i.id)}>Add Action</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
