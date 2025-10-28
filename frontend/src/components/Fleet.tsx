import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import { useAppStore, makeRange } from "../store";
import { useAuth } from "../auth";

type Vehicle = { id: number; reg: string; make: string; model: string; status: string };
type Booking = { id: number; vehicle_id: number; start_at: string; end_at: string; booked_by: string; purpose?: string };

export default function Fleet() {
  const { tenant, range } = useAppStore();
  const { user } = useAuth();
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [vehicleId, setVehicleId] = useState<number | null>(null);
  const [purpose, setPurpose] = useState("Run");
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [newV, setNewV] = useState<{ reg: string; make: string; model: string }>({ reg: "", make: "", model: "" });
  const [startAt, setStartAt] = useState<string>(() => localNowInput());
  const [durationMin, setDurationMin] = useState<number>(60);
  const [historyVehicle, setHistoryVehicle] = useState<number | 'all'>('all');
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editForm, setEditForm] = useState<{ reg: string; make: string; model: string; status: string }>({ reg: "", make: "", model: "", status: "AVAILABLE" });

  async function refresh() {
    const v = await api.listVehicles?.({ tenant });
    const { date_from, date_to } = makeRange(range);
    const b = await api.listBookings?.({ tenant, limit: 100, vehicle_id: historyVehicle === 'all' ? undefined : Number(historyVehicle), date_from, date_to });
    setVehicles(Array.isArray(v) ? v : []);
    setBookings(Array.isArray(b) ? b : []);
    if (v && v.length) setVehicleId(v[0].id);
  }
  useEffect(() => { refresh(); }, [tenant, range, historyVehicle]);

  async function createBooking() {
    if (!vehicleId) return;
    const start = startAt ? new Date(startAt) : new Date();
    const end = new Date(start.getTime() + Math.max(15, durationMin) * 60 * 1000);
    setErr(null); setMsg(null);
    const res = await api.createBooking?.({ vehicle_id: vehicleId, start_at: start.toISOString(), end_at: end.toISOString(), booked_by: "Dispatcher", purpose });
    if (!res) setErr("Failed to create booking (overlap?)"); else setMsg("Booked");
    await refresh();
  }

  async function addVehicle() {
    if (!newV.reg || !newV.make || !newV.model) { setErr("Please complete vehicle details"); return; }
    setErr(null); setMsg(null);
    const r = await api.createVehicle?.({ reg: newV.reg, make: newV.make, model: newV.model });
    if (!r) { setErr("Failed to add vehicle (duplicate?)"); return; }
    setMsg("Vehicle added");
    setNewV({ reg: "", make: "", model: "" });
    await refresh();
  }

  const regById = useMemo(() => Object.fromEntries(vehicles.map(v => [v.id, v.reg])), [vehicles]);
  const role = useMemo(() => {
    const links: any[] = (user?.tenants as any[]) || [];
    const match = links.find((t) => t.slug === tenant || String(t.id) === tenant || t.name === tenant);
    return (match?.role as string | undefined) || undefined;
  }, [user, tenant]);

  return (
    <div className="row two">
      <div className="card">
        <h3>Vehicles</h3>
        {msg && <div className="muted" style={{ marginBottom: 8 }}>{msg}</div>}
        {err && <div style={{ color: '#ef4444', marginBottom: 8 }}>{err}</div>}
        <table className="table">
          <thead><tr><th>Reg</th><th>Make/Model</th><th>Status</th>{(role==='owner'||role==='manager') && <th></th>}</tr></thead>
          <tbody>
            {vehicles.map(v => {
              const isEditing = editingId === v.id;
              if (isEditing) {
                return (
                  <tr key={v.id}>
                    <td><input value={editForm.reg} onChange={(e)=>setEditForm(f=>({ ...f, reg: e.target.value }))} /></td>
                    <td style={{ display:'flex', gap:6 }}>
                      <input value={editForm.make} onChange={(e)=>setEditForm(f=>({ ...f, make: e.target.value }))} style={{ width:160 }} />
                      <input value={editForm.model} onChange={(e)=>setEditForm(f=>({ ...f, model: e.target.value }))} style={{ width:160 }} />
                    </td>
                    <td>
                      <select value={editForm.status} onChange={(e)=>setEditForm(f=>({ ...f, status: e.target.value }))}>
                        <option value="AVAILABLE">AVAILABLE</option>
                        <option value="OUT">OUT</option>
                        <option value="SERVICE">SERVICE</option>
                      </select>
                    </td>
                    <td>
                      <div style={{ display:'flex', gap:6 }}>
                        <button className="primary" onClick={async ()=>{ await api.updateVehicle?.({ id: v.id, ...editForm }); setEditingId(null); await refresh(); }}>Save</button>
                        <button onClick={()=>setEditingId(null)}>Cancel</button>
                      </div>
                    </td>
                  </tr>
                );
              }
              return (
                <tr key={v.id}>
                  <td>{v.reg}</td>
                  <td>{v.make} {v.model}</td>
                  <td>{v.status}</td>
                  {(role==='owner'||role==='manager') && (
                    <td><button onClick={()=>{ setEditingId(v.id); setEditForm({ reg: v.reg, make: v.make, model: v.model, status: v.status }); }}>Edit</button></td>
                  )}
                </tr>
              );
            })}
            {!vehicles.length && <tr><td colSpan={3} className="muted">No vehicles.</td></tr>}
          </tbody>
        </table>
        <div style={{display:"grid", gap:8, marginTop:8, gridTemplateColumns:'repeat(auto-fit,minmax(180px,1fr))'}}>
          <select value={vehicleId ?? undefined} onChange={e=>setVehicleId(Number(e.target.value))}>
            {vehicles.map(v=> <option key={v.id} value={v.id}>{v.reg}</option>)}
          </select>
          <input value={purpose} onChange={e=>setPurpose(e.target.value)} placeholder="Purpose" />
          <input type="datetime-local" value={startAt} onChange={(e)=>setStartAt(e.target.value)} aria-label="Start at" />
          <select value={durationMin} onChange={(e)=>setDurationMin(Number(e.target.value))} aria-label="Duration minutes">
            <option value={30}>30 min</option>
            <option value={60}>1 hour</option>
            <option value={120}>2 hours</option>
            <option value={240}>4 hours</option>
          </select>
          <button className="primary" onClick={createBooking}>Book</button>
        </div>
        <div style={{display:'flex', gap:8, marginTop:8, flexWrap:'wrap'}}>
          <input value={newV.reg} onChange={e=>setNewV(v=>({ ...v, reg: e.target.value.toUpperCase() }))} placeholder="Reg (e.g., CA 123-456)" />
          <input value={newV.make} onChange={e=>setNewV(v=>({ ...v, make: e.target.value }))} placeholder="Make" />
          <input value={newV.model} onChange={e=>setNewV(v=>({ ...v, model: e.target.value }))} placeholder="Model" />
          <button onClick={addVehicle}>Add Vehicle</button>
        </div>
      </div>
      <div className="card">
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
          <h3>Recent Bookings</h3>
          <div style={{ display:'flex', gap:8, alignItems:'center' }}>
            <span className="label">Vehicle</span>
            <select value={historyVehicle} onChange={(e)=>setHistoryVehicle((e.target.value==='all'?'all':Number(e.target.value)))}>
              <option value="all">All</option>
              {vehicles.map(v=> <option key={v.id} value={v.id}>{v.reg}</option>)}
            </select>
          </div>
        </div>
        <table className="table">
          <thead><tr><th>Vehicle</th><th>Start</th><th>End</th><th>By</th><th>Purpose</th></tr></thead>
          <tbody>
            {bookings.map(b => (
              <tr key={b.id}><td>{regById[b.vehicle_id] || b.vehicle_id}</td><td>{new Date(b.start_at).toLocaleString()}</td><td>{new Date(b.end_at).toLocaleString()}</td><td>{b.booked_by}</td><td>{b.purpose}</td></tr>
            ))}
            {!bookings.length && <tr><td colSpan={5} className="muted">No bookings.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function localNowInput(): string {
  const d = new Date();
  d.setSeconds(0, 0);
  const p = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`;
}
