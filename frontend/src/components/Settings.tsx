// feat(settings): department targets editor (owner/manager only)
import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import { useAppStore } from "../store";
import { useAuth } from "../auth";

export default function Settings() {
  const { tenant } = useAppStore();
  const { user } = useAuth();
  const role: "owner" | "manager" | "staff" | "viewer" | undefined = useMemo(() => {
    const links: any[] = (user?.tenants as any[]) || [];
    const match = links.find((t) => t.slug === tenant || String(t.id) === tenant || t.name === tenant);
    return match?.role as any;
  }, [user, tenant]);

  const [targets, setTargets] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<Record<string, boolean>>({});

  useEffect(() => {
    let alive = true;
    (async () => {
      setLoading(true);
      const list = await api.listTargets({ tenant });
      const map: Record<string, number> = {}; (Array.isArray(list)?list:[]).forEach((x:any)=> map[x.dept] = Number(x.target)||0);
      if (alive) { setTargets(map); setLoading(false); }
    })();
    return () => { alive = false; };
  }, [tenant]);

  if (!role || (role !== 'owner' && role !== 'manager')) {
    return <div className="card"><h3>Settings</h3><div className="muted">You need manager or owner role to edit targets.</div></div>;
  }

  const labels = ['Rooms','F&B','Spa','Conference'];
  return (
    <div className="card">
      <h3>Department Monthly Targets</h3>
      {loading && <div className="muted">Loading...</div>}
      {!loading && (
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(220px,1fr))', gap:10, marginTop:8 }}>
          {labels.map((dept) => (
            <div key={dept} className="field">
              <label>{dept} target (ZAR)</label>
              <input value={String(targets[dept] ?? 0)} onChange={(e)=>setTargets(prev=>({ ...prev, [dept]: Number(e.target.value||0) }))} />
              <div>
                <button onClick={async ()=>{ setSaving(s=>({ ...s, [dept]: true })); try { await api.upsertTarget({ tenant, dept, target: Number(targets[dept]||0) }); } finally { setSaving(s=>({ ...s, [dept]: false })); } }} disabled={!!saving[dept]}>Save</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}