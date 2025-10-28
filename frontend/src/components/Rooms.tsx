import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import { useAppStore, makeRange } from "../store";

type Room = { id: number; name: string; status?: string; booked_now?: number };
type RoomBooking = { id: number; room_id: number; start_at: string; end_at: string; booked_by?: string; purpose?: string };

export default function Rooms() {
  const { tenant, range } = useAppStore();
  const [rooms, setRooms] = useState<Room[]>([]);
  const [bookings, setBookings] = useState<RoomBooking[]>([]);
  const [upcoming, setUpcoming] = useState<RoomBooking[]>([]);
  const [roomId, setRoomId] = useState<number | null>(null);
  const [purpose, setPurpose] = useState("Meeting");
  const [startAt, setStartAt] = useState<string>(() => localNowInput());
  const [duration, setDuration] = useState<string>("1 hour");
  const [adding, setAdding] = useState(false);
  const [newName, setNewName] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);

  async function refresh() {
    const r = await api.listRooms({ tenant });
    setRooms(Array.isArray(r) ? r : []);
    if (r && r.length && !roomId) setRoomId(r[0].id);
    const { date_from, date_to } = makeRange(range);
    const b = await api.listRoomBookings({ tenant, limit: 100, room_id: undefined, date_from, date_to });
    setBookings(Array.isArray(b) ? b : []);
    try {
      const up = await api.listRoomUpcoming({ tenant, hours: 48 });
      setUpcoming(Array.isArray(up)?up:[]);
    } catch { setUpcoming([]); }
  }
  useEffect(() => { refresh(); }, [tenant, range]);

  const nameById = useMemo(() => Object.fromEntries(rooms.map(r => [r.id, r.name])), [rooms]);

  async function createBooking() {
    if (!roomId) return;
    setErr(null); setMsg(null);
    // Ensure UTC ISO to avoid timezone mismatches with DB CURRENT_TIMESTAMP
    const iso = new Date(startAt).toISOString();
    const res = await api.createRoomBooking({ tenant, room_id: roomId, start_at: iso, duration: canonicalDuration(duration), purpose, booked_by: "Dispatcher" });
    if (!res) setErr("Failed to create booking (overlap?)"); else setMsg("Booked");
    await refresh();
  }

  async function addRoom() {
    const n = newName.trim();
    if (!n) { setErr("Room name required"); return; }
    setAdding(true); setErr(null); setMsg(null);
    try {
      const r = await api.createRoom({ tenant, name: n });
      if (!r) setErr("Failed to add room"); else setMsg("Room added");
      setNewName("");
    } finally {
      setAdding(false);
      await refresh();
    }
  }

  return (
    <div className="row two">
      <div className="card">
        <h3>Rooms</h3>
        <Overview rooms={rooms} bookings={bookings} />
        {msg && <div className="muted" style={{ marginBottom: 8 }}>{msg}</div>}
        {err && <div style={{ color: '#ef4444', marginBottom: 8 }}>{err}</div>}
        <RoomGrid rooms={rooms} onUpdated={refresh} />
        <div style={{display:'grid', gap:8, gridTemplateColumns:'repeat(auto-fit,minmax(180px,1fr))', marginTop:8}}>
          <select value={roomId ?? undefined} onChange={(e)=>setRoomId(Number(e.target.value))}>
            {rooms.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
          </select>
          <input value={purpose} onChange={(e)=>setPurpose(e.target.value)} placeholder="Purpose" />
          <input type="datetime-local" value={startAt} onChange={(e)=>setStartAt(e.target.value)} />
          <select value={duration} onChange={(e)=>setDuration(e.target.value)}>
            <option>1 hour</option>
            <option>2 hours</option>
            <option>3 hours</option>
            <option>Half day</option>
            <option>Full day</option>
            <option>Night</option>
          </select>
          <button className="primary" onClick={createBooking}>Book</button>
        </div>
        <div style={{display:'flex', gap:8, marginTop:8, flexWrap:'wrap'}}>
          <input value={newName} onChange={(e)=>setNewName(e.target.value)} placeholder="Room name" />
          <button onClick={addRoom} disabled={adding}>Add Room</button>
        </div>
      </div>
      <div className="card">
        <h3>Scheduled & Recent Bookings</h3>
        <table className="table">
          <thead><tr><th>Room</th><th>Start</th><th>End</th><th>By</th><th>Purpose</th></tr></thead>
          <tbody>
            {bookings.map(b => (
              <tr key={b.id}><td>{nameById[b.room_id] || b.room_id}</td><td>{new Date(b.start_at).toLocaleString()}</td><td>{new Date(b.end_at).toLocaleString()}</td><td>{b.booked_by}</td><td>{b.purpose}</td></tr>
            ))}
            {!bookings.length && <tr><td colSpan={5} className="muted">No bookings.</td></tr>}
          </tbody>
        </table>
        {roomId && (
          <>
            <h3 style={{ marginTop: 12 }}>Selected Room History</h3>
            <table className="table">
              <thead><tr><th>Start</th><th>End</th><th>Amount</th><th>By</th><th>Purpose</th></tr></thead>
              <tbody>
                {bookings.filter(b=>b.room_id===roomId).map(b => (
                  <tr key={`h-${b.id}`}><td>{new Date(b.start_at).toLocaleString()}</td><td>{new Date(b.end_at).toLocaleString()}</td><td>{(b as any).amount ?? ''}</td><td>{b.booked_by}</td><td>{b.purpose}</td></tr>
                ))}
                {bookings.filter(b=>b.room_id===roomId).length===0 && <tr><td colSpan={5} className="muted">No history for this room.</td></tr>}
              </tbody>
            </table>
          </>
        )}
        <h3 style={{ marginTop: 12 }}>Upcoming (48h)</h3>
        <table className="table">
          <thead><tr><th>Room</th><th>Start</th><th>End</th><th>By</th><th>Purpose</th></tr></thead>
          <tbody>
            {upcoming.map(b => (
              <tr key={`u-${b.id}`}><td>{nameById[b.room_id] || b.room_id}</td><td>{new Date(b.start_at).toLocaleString()}</td><td>{new Date(b.end_at).toLocaleString()}</td><td>{b.booked_by}</td><td>{b.purpose}</td></tr>
            ))}
            {!upcoming.length && <tr><td colSpan={5} className="muted">No upcoming check-ins/outs.</td></tr>}
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

function canonicalDuration(label: string): string {
  const l = (label || '').toLowerCase();
  if (l.includes('2')) return '2 hours';
  if (l.includes('3')) return '3 hours';
  if (l.includes('half')) return 'half_day';
  if (l.includes('full')) return 'full_day';
  if (l.includes('night')) return 'night';
  return '1 hour';
}

function Overview({ rooms, bookings }: { rooms: Room[]; bookings: RoomBooking[] }) {
  const occ = rooms.filter(r => (r as any).booked_now).length;
  const ooo = rooms.filter(r => Number((r as any).out_of_order || 0) === 1).length;
  const vacant = rooms.length - occ - ooo;
  // Avg stay duration & rate (rough, based on bookings)
  const durations = bookings.map(b => (new Date(b.end_at).getTime() - new Date(b.start_at).getTime()) / 3600000);
  const avgStay = durations.length ? Math.round(durations.reduce((a,b)=>a+b,0)/durations.length) : 0;
  const rates = (bookings as any[]).map(b => Number(b.amount || 0));
  const avgRate = rates.length ? Math.round(rates.reduce((a,b)=>a+b,0)/Math.max(1, bookings.length)) : 0;
  const Card = ({ title, value, suffix }: { title: string; value: number; suffix?: string }) => (
    <div className="card kpi"><h4>{title}</h4><div className="big">{suffix ? `${value}${suffix}` : value}</div><div className="sub">Rooms</div></div>
  );
  return (
    <div className="row kpis" style={{ marginBottom: 8 }}>
      <Card title="Occupied" value={occ} />
      <Card title="Vacant" value={vacant} />
      <Card title="Out of Order" value={ooo} />
      <div className="card kpi"><h4>Avg Stay</h4><div className="big">{avgStay}h</div><div className="sub">Based on bookings</div></div>
      <div className="card kpi"><h4>Avg Rate</h4><div className="big">R {avgRate}</div><div className="sub">Approx per booking</div></div>
    </div>
  );
}

function RoomGrid({ rooms, onUpdated }: { rooms: Room[]; onUpdated?: ()=>void }) {
  const color = (r: any) => {
    if (Number(r.out_of_order || 0) === 1) return '#64748b';
    if (r.booked_now) return '#ef4444';
    const hk = String(r.housekeeping_status || 'CLEAN').toUpperCase();
    if (hk === 'CLEANING') return '#f59e0b';
    return '#22c55e';
  };
  return (
    <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(180px,1fr))', gap:10, marginTop:8 }}>
      {rooms.map((r:any)=>(
        <div key={r.id} className="card" style={{ borderColor:'#22304f', background:'#0b1324', boxShadow:`inset 4px 0 0 0 ${color(r)}` }}>
          <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
            <strong>{r.name}</strong>
            <span style={{ width:10, height:10, borderRadius:999, background: color(r) }}></span>
          </div>
          <div className="muted" style={{ marginTop:6 }}>Status: {r.status || 'AVAILABLE'} {Number(r.out_of_order||0)===1?'(OOO)':''}</div>
          {r.booked_now ? (
            <div style={{ marginTop:6 }}>
              <div className="muted">Guest</div>
              <div>{r.current_guest || '—'}</div>
              <div className="muted">Check-in/out</div>
              <div>{r.current_checkin ? new Date(r.current_checkin).toLocaleString() : '—'} → {r.current_checkout ? new Date(r.current_checkout).toLocaleString() : '—'}</div>
            </div>
          ) : (
            <div style={{ marginTop:6 }} className="muted">Not occupied</div>
          )}
          <RoomActions r={r} onUpdated={onUpdated} />
        </div>
      ))}
    </div>
  );
}

function RoomActions({ r, onUpdated }: { r: any; onUpdated?: ()=>void }) {
  const [hk, setHk] = useState<string>(String(r.housekeeping_status || 'CLEAN'));
  const [ooo, setOoo] = useState<boolean>(Boolean(Number(r.out_of_order || 0)));
  const { tenant } = useAppStore();
  return (
    <div style={{ display:'flex', gap:6, marginTop:8, alignItems:'center', flexWrap:'wrap' }}>
      <select value={hk} onChange={e=>setHk(e.target.value)} aria-label="Housekeeping status">
        <option value="CLEAN">CLEAN</option>
        <option value="CLEANING">CLEANING</option>
        <option value="INSPECTED">INSPECTED</option>
      </select>
      <label style={{ display:'flex', gap:6, alignItems:'center' }}>
        <input type="checkbox" checked={ooo} onChange={e=>setOoo(e.target.checked)} /> Out of Order
      </label>
      <button onClick={async ()=>{ await api.updateRoom({ tenant, id: Number(r.id), housekeeping_status: hk, out_of_order: ooo }); onUpdated && onUpdated(); }}>
        Update
      </button>
    </div>
  );
}
