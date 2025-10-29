import { useEffect, useState } from "react";
import { api } from "../api";
import { useAppStore } from "../store";
import { useAuth } from "../auth";
import Select from "../atom/Select";

type HandoverRow = {
  id?: number | string;
  date?: string;     // ISO date
  outlet?: string;
  shift?: string;
  covers?: number;
};

export default function Handovers() {
  const { tenant } = useAppStore();
  const { user } = useAuth();
  const [rows, setRows] = useState<HandoverRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState<{ date: string; outlet: string; shift: string; covers: string }>({
    date: "",
    outlet: "",
    shift: "AM",
    covers: "0",
  });
  const [editingId, setEditingId] = useState<number | string | null>(null);
  const [editForm, setEditForm] = useState<{ date: string; outlet: string; shift: "AM" | "PM"; covers: string }>({ date: "", outlet: "", shift: "AM", covers: "0" });

  const role = (() => {
    const links: any[] = ((user as any)?.tenants) || [];
    const t = links.find((t) => t.slug === tenant || String(t.id) === tenant || t.name === tenant);
    return (t?.role as string | undefined) || undefined;
  })();

  useEffect(() => {
    let alive = true;
    (async () => {
      setLoading(true);
      const data = await api.listHandovers({ tenant, limit: 10 });
      if (!alive) return;
      setRows(Array.isArray(data) ? data : []);
      setLoading(false);
    })();
    return () => { alive = false; };
  }, [tenant]);

  return (
    <div className="card">
      <h3>Recent Handovers</h3>

      <form
        aria-label="Create Handover"
        onSubmit={async (e) => {
          e.preventDefault();
          if (!form.date || !form.outlet) return;
          const coversNum = Number(form.covers);
          const safeCovers = Number.isFinite(coversNum) && coversNum >= 0 ? coversNum : 0;
          setSaving(true);
          await api.createHandover({
            tenant,
            date: form.date,
            outlet: form.outlet.trim(),
            shift: form.shift,
            covers: safeCovers,
          });
          const data = await api.listHandovers({ tenant, limit: 10 });
          setRows(Array.isArray(data) ? data : []);
          setSaving(false);
          setForm((f) => ({ ...f, outlet: "", covers: "0" }));
        }}
        style={{ marginBottom: 12 }}
      >
        <div className="form-grid">
          <div className="field">
            <label htmlFor="handover-date">Date</label>
            <input
              id="handover-date"
              aria-label="Date"
              type="date"
              value={form.date}
              onChange={(e) => setForm((f) => ({ ...f, date: e.target.value }))}
              required
            />
          </div>
          <div className="field">
            <label htmlFor="handover-outlet">Outlet</label>
            <input
              id="handover-outlet"
              aria-label="Outlet"
              placeholder="e.g., Café Grill"
              value={form.outlet}
              onChange={(e) => setForm((f) => ({ ...f, outlet: e.target.value }))}
              required
            />
          </div>
          <div className="field">
            <label htmlFor="handover-shift">Shift</label>
            <Select
              id="handover-shift"
              options={[{ label: "AM", value: "AM" as const }, { label: "PM", value: "PM" as const }]}
              value={form.shift as "AM" | "PM"}
              onChange={(v) => setForm((f) => ({ ...f, shift: v }))}
            />
          </div>
          <div className="field">
            <label htmlFor="handover-covers">Covers</label>
            <input
              id="handover-covers"
              aria-label="Covers"
              type="number"
              min={0}
              inputMode="numeric"
              value={form.covers}
              onChange={(e) => setForm((f) => ({ ...f, covers: e.target.value }))}
            />
          </div>
        </div>
        <div style={{ marginTop: 10, display: "flex", gap: 8 }}>
          <button type="submit" className="primary" disabled={saving} aria-label="Save handover">
            {saving ? "Saving..." : "Add Handover"}
          </button>
        </div>
      </form>

      <table className="table">
        <thead>
          <tr><th>Date</th><th>Shift</th><th>Outlet</th><th>Covers</th></tr>
        </thead>
        <tbody>
          {loading && (
            <tr><td colSpan={4} className="muted">Loading...</td></tr>
          )}
          {!loading && rows.map((r) => {
            const isEditing = editingId === r.id;
            if (isEditing) {
              return (
                <tr key={String(r.id ?? `${r.date}-${r.shift}-${r.outlet}`)}>
                  <td>
                    <input type="date" aria-label="Date" value={editForm.date} onChange={(e)=>setEditForm(f=>({ ...f, date: e.target.value }))} />
                  </td>
                  <td>
                    <Select id={`edit-shift-${r.id}`} options={[{label:'AM', value:'AM' as const},{label:'PM', value:'PM' as const}]} value={editForm.shift} onChange={(v)=>setEditForm(f=>({ ...f, shift: v }))} />
                  </td>
                  <td>
                    <input aria-label="Outlet" value={editForm.outlet} onChange={(e)=>setEditForm(f=>({ ...f, outlet: e.target.value }))} />
                  </td>
                  <td>
                    <div style={{ display:'flex', gap:6, alignItems:'center' }}>
                      <input type="number" min={0} aria-label="Covers" value={editForm.covers} onChange={(e)=>setEditForm(f=>({ ...f, covers: e.target.value }))} style={{ width: 100 }} />
                      <button onClick={async ()=>{
                        const cid = Number(r.id);
                        const coversNum = Number(editForm.covers);
                        const safeCovers = Number.isFinite(coversNum) && coversNum >= 0 ? coversNum : 0;
                        await api.updateHandover({ tenant, id: cid, date: editForm.date, outlet: editForm.outlet.trim(), shift: editForm.shift, covers: safeCovers });
                        const data = await api.listHandovers({ tenant, limit: 10 });
                        setRows(Array.isArray(data) ? data : []);
                        setEditingId(null);
                      }} className="primary" aria-label="Save handover">Save</button>
                      <button onClick={()=>setEditingId(null)} aria-label="Cancel edit">Cancel</button>
                    </div>
                  </td>
                </tr>
              );
            }
            return (
              <tr key={String(r.id ?? `${r.date}-${r.shift}-${r.outlet}`)}>
                <td>{r.date ? new Date(r.date).toLocaleDateString() : ""}</td>
                <td>{r.shift ?? ""}</td>
                <td>{r.outlet ?? ""}</td>
                <td>
                  <div style={{ display:'flex', gap:8, alignItems:'center' }}>
                    {Number.isFinite(Number(r.covers)) ? Number(r.covers) : 0}
                    {(role === 'manager' || role === 'owner') && (
                      <button onClick={()=>{
                        setEditingId(r.id ?? "");
                        setEditForm({
                          date: (r.date || "").slice(0,10),
                          outlet: r.outlet || "",
                          shift: ((r.shift as any) === 'PM' ? 'PM' : 'AM'),
                          covers: String(Number.isFinite(Number(r.covers)) ? Number(r.covers) : 0),
                        });
                      }} aria-label="Edit handover">Edit</button>
                    )}
                  </div>
                </td>
              </tr>
            );
          })}
          {!loading && rows.length === 0 && (
            <tr><td colSpan={4} className="muted">No handovers yet.</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
