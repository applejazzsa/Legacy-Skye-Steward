// feat(rooms): clean duplication, add amount + summary totals, fix status colors and glyphs
import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import { useAppStore, makeRange } from "../store";
import { formatZAR } from "../util/currency";
import Modal from "./Modal";
import Toasts, { Toast } from "./Toast";
import RoomsCalendar from "./RoomsCalendar";

type Room = { id: number; name: string; status?: string; booked_now?: number; inspected_at?: string; housekeeping_status?: string; out_of_order?: number | boolean; current_guest?: string; current_checkin?: string; current_checkout?: string; base_rate?: number };
type RoomBooking = { id: number; room_id: number; start_at: string; end_at: string; booked_by?: string; purpose?: string; amount?: number };

export default function Rooms() {
  const { tenant, range } = useAppStore();
  const [rooms, setRooms] = useState<Room[]>([]);
  const [bookings, setBookings] = useState<RoomBooking[]>([]);
  const [upcoming, setUpcoming] = useState<RoomBooking[]>([]);
  const [summary, setSummary] = useState<{ day: number; week: number; month: number; year: number }>({ day: 0, week: 0, month: 0, year: 0 });
  const [roomId, setRoomId] = useState<number | null>(null);
  const [purpose, setPurpose] = useState("Meeting");
  const [purposeMode, setPurposeMode] = useState<"Meeting"|"Overnight"|"DayUse"|"Custom">("Meeting");
  const [startAt, setStartAt] = useState<string>(() => localNowInput());
  const [duration, setDuration] = useState<string>("30m");
  const [amount, setAmount] = useState<string>("");
  const [availabilityMsg, setAvailabilityMsg] = useState<string>("");
  const [tasksByRoom, setTasksByRoom] = useState<Record<number, number>>({});
  const [adding, setAdding] = useState(false);
  const [newName, setNewName] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [oooOpen, setOooOpen] = useState<{ open: boolean; roomId: number | null; reason: string; eta: string }>({ open: false, roomId: null, reason: "", eta: "" });

  async function refresh() {
    const r = await api.listRooms({ tenant });
    setRooms(Array.isArray(r) ? (r as Room[]) : []);
    if (r && (r as any[]).length && !roomId) setRoomId((r as any[])[0].id as number);
    const { date_from, date_to } = makeRange(range);
    const b = await api.listRoomBookings({ tenant, limit: 100, room_id: undefined, date_from, date_to });
    setBookings(Array.isArray(b) ? (b as RoomBooking[]) : []);
    try {
      const up = await api.listRoomUpcoming({ tenant, hours: 48 });
      setUpcoming(Array.isArray(up) ? (up as RoomBooking[]) : []);
    } catch { setUpcoming([]); }
    try {
      const s = await api.roomSummary({ tenant });
      if (s) setSummary({ day: safeNum((s as any).day), week: safeNum((s as any).week), month: safeNum((s as any).month), year: safeNum((s as any).year) });
    } catch { setSummary({ day: 0, week: 0, month: 0, year: 0 }); }
    try {
      // Load in-progress HK tasks per room for quick complete
      const list = await api.listHousekeepingTasks({ tenant, status: "IN_PROGRESS" });
      const map: Record<number, number> = {};
      (list || []).forEach((t: any) => { if (Number.isFinite(+t.room_id)) map[+t.room_id] = t.id; });
      setTasksByRoom(map);
    } catch { setTasksByRoom({}); }
  }
  useEffect(() => { refresh(); }, [tenant, range]);

  const nameById = useMemo(() => Object.fromEntries(rooms.map(r => [r.id, r.name])), [rooms]);

  useEffect(() => {
    (async () => {
      try {
        setAvailabilityMsg("");
        if (!roomId) return;
        const endIso = computeEndISO(startAt, duration);
        if (!endIso) return;
        const mins = durationMinutes(duration);
        if (mins < 30) { setAvailabilityMsg("Minimum duration 30 minutes"); return; }
        const r = rooms.find(r=>r.id===roomId);
        if (r && String(r.status||'').toUpperCase()==='OUT_OF_ORDER') { setAvailabilityMsg("Room is Out of Order"); return; }
        const startIso = new Date(startAt).toISOString();
        const chk = await api.checkRoomAvailability({ tenant, room_id: roomId, start: startIso, end: endIso });
        if (chk && chk.available === false) {
          const reason = String(chk.reason||'conflict');
          setAvailabilityMsg(reason === 'overlap' ? 'Conflicting booking' : (reason === 'out_of_order' ? 'Room is Out of Order' : 'Not available'));
        } else {
          setAvailabilityMsg("");
        }
      } catch {}
    })();
  }, [tenant, roomId, startAt, duration, rooms]);

  async function createBooking() {
    if (!roomId) return;
    setErr(null); setMsg(null);
    const startIso = new Date(startAt).toISOString();
    const endIso = computeEndISO(startAt, duration);
    if (!endIso) { setErr('Invalid start/end'); return; }
    const minutes = durationMinutes(duration);
    if (minutes < 30) { setErr('Minimum duration is 30 minutes'); return; }
    const room = rooms.find(r=>r.id===roomId);
    if (room && String(room.status||'').toUpperCase()==='OUT_OF_ORDER') { setErr('Room is out of order'); return; }
    const avail = await api.checkRoomAvailability({ tenant, room_id: roomId, start: startIso, end: endIso });
    if (avail && avail.available === false) { setErr(avail.reason || 'Not available'); return; }
    const amtNum = parseFloat(amount);
    const payload: any = { tenant, room_id: roomId, start: startIso, end: endIso, purpose, booked_by: 'Dispatcher', amount: Number.isFinite(amtNum) ? amtNum : undefined };
    const res = await api.createRoomBooking(payload);
    if (!res) setErr('Failed to create booking (overlap or invalid input)'); else setMsg('Booked');
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
    <>
    <div className="row two">
      <div className="card">
        <div style={{display:'flex', alignItems:'center', justifyContent:'space-between'}}>
          <h3>Rooms</h3>
          <button onClick={()=>{
            const el = document.getElementById('rooms-calendar-inline');
            if (el) { el.style.display = el.style.display==='none' ? 'block' : 'none'; }
          }}>Calendar</button>
        </div>
        <Overview rooms={rooms} bookings={bookings} />
        <div className="row kpis" style={{ marginTop: 8 }}>
          <Kpi title="Today's Total" value={summary.day} money />
          <Kpi title="This Week" value={summary.week} money />
          <Kpi title="This Month" value={summary.month} money />
          <Kpi title="This Year" value={summary.year} money />
        </div>
        {msg && <div className="muted" style={{ marginTop: 8 }}>{msg}</div>}
        {err && <div style={{ color: '#ef4444', marginTop: 8 }}>{err}</div>}
        <RoomGrid rooms={rooms} onUpdated={refresh} onOoo={(rid)=> setOooOpen({ open: true, roomId: rid, reason: "", eta: "" })} addToast={(t)=>setToasts((x)=>[...x,{ id: String(Date.now()), ...t }])} />
        <div style={{display:'grid', gap:8, gridTemplateColumns:'repeat(auto-fit,minmax(180px,1fr))', marginTop:8}}>
          <select value={roomId ?? undefined} onChange={(e)=>setRoomId(Number(e.target.value))} aria-label="Select room">
            {rooms.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
          </select>
          <select value={purposeMode} onChange={(e)=>{ const v = e.target.value as any; setPurposeMode(v); if (v !== 'Custom') setPurpose(v); }} aria-label="Purpose">
            <option value="Meeting">Meeting</option>
            <option value="Overnight">Overnight</option>
            <option value="DayUse">DayUse</option>
            <option value="Custom">Custom</option>
          </select>
          {purposeMode==='Custom' && (
            <input value={purpose} onChange={(e)=>setPurpose(e.target.value)} placeholder="Custom purpose" aria-label="Custom purpose" />
          )}
          <input type="datetime-local" value={startAt} onChange={(e)=>setStartAt(e.target.value)} aria-label="Start at" />
          <select value={duration} onChange={(e)=>setDuration(e.target.value)} aria-label="Booking duration">
            <option value="15m">15m</option>
            <option value="30m">30m</option>
            <option value="1h">1h</option>
            <option value="2h">2h</option>
            <option value="overnight">Overnight</option>
          </select>
          <input inputMode="decimal" placeholder={previewAmountLabel(rooms.find(r=>r.id===roomId), duration)} value={amount} onChange={(e)=>setAmount(e.target.value)} aria-label="Amount" />
          {availabilityMsg && <div className="muted" style={{ gridColumn:'1 / -1', color:'#ef4444' }}>{availabilityMsg}</div>}
          <button className="primary" onClick={createBooking}>Book</button>
        </div>
        <div style={{display:'flex', gap:8, marginTop:8, flexWrap:'wrap'}}>
          <input value={newName} onChange={(e)=>setNewName(e.target.value)} placeholder="Room name" aria-label="New room name" />
          <button onClick={addRoom} disabled={adding}>Add Room</button>
        </div>
      </div>
      <div id="rooms-calendar-inline" style={{display:'none', marginTop:12}}>
        {/* inline fallback for /rooms/calendar */}
        {/** @ts-ignore */}
        <RoomsCalendar />
      </div>
      <div className="card">
        <h3>Scheduled & Recent Bookings</h3>
        <table className="table" aria-label="Room bookings table">
          <thead><tr><th>Room</th><th>Start</th><th>End</th><th>By</th><th>Purpose</th><th>Amount</th></tr></thead>
          <tbody>
            {bookings.map(b => (
              <tr key={b.id}><td>{nameById[b.room_id] || b.room_id}</td><td>{safeDate(b.start_at)}</td><td>{safeDate(b.end_at)}</td><td>{b.booked_by}</td><td>{b.purpose}</td><td>{formatZAR(safeNum(b.amount))}</td></tr>
            ))}
            {!bookings.length && <tr><td colSpan={6} className="muted">No bookings.</td></tr>}
          </tbody>
        </table>
        {!!upcoming.length && (
          <div style={{ marginTop: 12 }}>
            <h3>Upcoming (48h)</h3>
            <ul className="muted">
              {upcoming.map(u => (
                <li key={u.id}>{nameById[u.room_id] || u.room_id}: {safeDate(u.start_at)} → {safeDate(u.end_at)} ({u.purpose || "Booking"})</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
    {/* OOO Modal */}
    <Modal
      open={oooOpen.open}
      title="Mark Out of Order"
      onClose={()=>setOooOpen({ open:false, roomId:null, reason:"", eta:"" })}
      footer={
        <div style={{ display:'flex', gap:8, justifyContent:'flex-end' }}>
          <button onClick={()=>setOooOpen({ open:false, roomId:null, reason:"", eta:"" })}>Cancel</button>
          <button className="primary" onClick={async ()=>{
            if (!oooOpen.roomId) return;
            const rid = oooOpen.roomId;
            const res = await api.markOutOfOrder({ tenant, id: rid, reason: oooOpen.reason, eta: oooOpen.eta || undefined });
            if (res) {
              setToasts((x)=>[...x,{ id:String(Date.now()), kind:'success', msg:'Room marked Out of Order' }]);
              setRooms((rs)=>rs.map((r)=> r.id===rid ? { ...r, status:'OUT_OF_ORDER', out_of_order:1 } as any : r));
              setOooOpen({ open:false, roomId:null, reason:"", eta:"" });
            } else {
              setToasts((x)=>[...x,{ id:String(Date.now()), kind:'error', msg:'Failed to set Out of Order' }]);
            }
          }}>Confirm</button>
        </div>
      }
    >
      <div style={{ display:'grid', gap:8 }}>
        <label>
          <div className="label">Reason</div>
          <input value={oooOpen.reason} onChange={(e)=>setOooOpen((s)=>({ ...s, reason:e.target.value }))} placeholder="e.g. AC broken" />
        </label>
        <label>
          <div className="label">ETA (optional)</div>
          <input type="datetime-local" value={oooOpen.eta} onChange={(e)=>setOooOpen((s)=>({ ...s, eta:e.target.value }))} />
        </label>
      </div>
    </Modal>
    <Toasts toasts={toasts} onDismiss={(id)=>setToasts((x)=>x.filter(t=>t.id!==id))} />
    </>
  );
}

function Overview({ rooms, bookings }: { rooms: Room[]; bookings: RoomBooking[] }) {
  const occ = rooms.filter((r: any) => Number(r.booked_now || 0) === 1).length;
  const ooo = rooms.filter((r: any) => Number(r.out_of_order || 0) === 1).length;
  const vacant = Math.max(0, rooms.length - occ - ooo);
  const durations = bookings.map(b => (new Date(b.end_at).getTime() - new Date(b.start_at).getTime()) / 3600000).filter(isFinite);
  const rates = bookings.map(b => safeNum(b.amount)).filter(isFinite);
  const avgStay = durations.length ? Math.round(durations.reduce((a,b)=>a+b,0)/Math.max(1, durations.length)) : 0;
  const avgRate = rates.length ? Math.round(rates.reduce((a,b)=>a+b,0)/Math.max(1, bookings.length)) : 0;
  return (
    <div className="row kpis" style={{ marginBottom: 8 }}>
      <Kpi title="Occupied" value={occ} />
      <Kpi title="Vacant" value={vacant} />
      <Kpi title="Out of Order" value={ooo} />
      <Kpi title="Avg Stay" value={avgStay} suffix="h" />
      <Kpi title="Avg Rate" value={avgRate} money />
    </div>
  );
}

function Kpi({ title, value, suffix, money }: { title: string; value: number; suffix?: string; money?: boolean }) {
  const v = Number.isFinite(value) ? value : 0;
  return (
    <div className="card kpi"><h4>{title}</h4><div className="big">{money ? formatZAR(v) : (suffix ? `${v}${suffix}` : v)}</div><div className="sub">Rooms</div></div>
  );
}

function RoomGrid({ rooms, onUpdated, onOoo, addToast }: { rooms: Room[]; onUpdated?: ()=>void; onOoo?: (roomId:number)=>void; addToast?: (t: Toast)=>void }) {
  const color = (r: any) => {
    if (Number(r.out_of_order || 0) === 1) return '#64748b';
    if (Number(r.booked_now || 0) === 1) return '#ef4444';
    const hk = String(r.housekeeping_status || 'CLEAN').toUpperCase();
    if (hk === 'CLEANING') return '#f59e0b';
    return '#22c55e';
  };
  const statusPill = (s?: string) => {
    const v = String(s||'AVAILABLE').toUpperCase();
    const styles: Record<string,string> = {
      'AVAILABLE':'#16a34a', 'OCCUPIED':'#ef4444', 'CLEANING':'#f59e0b', 'OUT_OF_ORDER':'#64748b', 'RESERVED':'#8b5cf6'
    };
    const bg = styles[v] || '#16a34a';
    return <span aria-label={`Status ${v}`} style={{ padding:'2px 8px', borderRadius:999, background:bg, color:'#fff', fontSize:12 }}>{v.replace('_',' ')}</span>;
  };
  return (
    <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(180px,1fr))', gap:10, marginTop:8 }}>
      {rooms.map((r:any)=>(
        <div key={r.id} className="card" tabIndex={0} onKeyDown={(e)=>{
          const k = e.key.toLowerCase();
          if (k==='o') { onOoo && onOoo(Number(r.id)); }
          if (k==='u') { const btn = document.getElementById(`upd-${r.id}`) as HTMLButtonElement | null; btn?.click(); }
        }} style={{ borderColor:'#22304f', background:'#0b1324', boxShadow:`inset 4px 0 0 0 ${color(r)}` }}>
          <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', gap:8 }}>
            <strong title={r.inspected_at ? `Inspected ${safeDate(r.inspected_at)}` : undefined}>{r.name}</strong>
            {statusPill(r.status)}
          </div>
          <div className="muted" style={{ marginTop:6 }}>Status: {r.status || 'AVAILABLE'} {Number(r.out_of_order||0)===1?'(OOO)':''}</div>
          {Number(r.booked_now || 0) === 1 ? (
            <div style={{ marginTop:6 }}>
              <div className="muted">Guest</div>
              <div>{r.current_guest || '-'}</div>
              <div className="muted">Check-in/out</div>
              <div>{r.current_checkin ? safeDate(r.current_checkin) : '-'} → {r.current_checkout ? safeDate(r.current_checkout) : '-'}</div>
            </div>
          ) : (
            <div style={{ marginTop:6 }} className="muted">Not occupied</div>
          )}
          <RoomActions r={r} onUpdated={onUpdated} onOoo={onOoo} addToast={addToast} />
          <RoomStateButtons r={r} onUpdated={onUpdated} />
        </div>
      ))}
    </div>
  );
}

function RoomActions({ r, onUpdated, onOoo, addToast }: { r: any; onUpdated?: ()=>void; onOoo?: (roomId:number)=>void; addToast?: (t: Toast)=>void }) {
  const [hk, setHk] = useState<string>('CLEAN');
  const [ooo, setOoo] = useState<boolean>(Boolean(Number(r.out_of_order || 0)));
  const [pending, setPending] = useState<boolean>(false);
  const { tenant } = useAppStore();
  return (
    <div style={{ display:'flex', gap:6, marginTop:8, alignItems:'center', flexWrap:'wrap' }}>
      <select value={hk} onChange={e=>setHk(e.target.value)} aria-label="Housekeeping status">
        <option value="DIRTY">DIRTY</option>
        <option value="IN_PROGRESS">IN_PROGRESS</option>
        <option value="CLEAN">CLEAN</option>
      </select>
      <label style={{ display:'flex', gap:6, alignItems:'center' }}>
        <input type="checkbox" checked={ooo} onChange={(e)=>{
          const next = e.target.checked;
          setOoo(next);
          if (next) { onOoo && onOoo(Number(r.id)); }
          else {
            // Back in service
            (async()=>{ setPending(true); try {
              const res = await api.backInService({ tenant, id: Number(r.id) });
              if (res) { addToast && addToast({ id:String(Date.now()), kind:'success', msg:'Back in service' }); onUpdated && onUpdated(); }
              else { addToast && addToast({ id:String(Date.now()), kind:'error', msg:'Failed to set back in service' }); }
            } finally { setPending(false); } })();
          }
        }} /> Out of Order
      </label>
      <button id={`upd-${r.id}`} disabled={pending} onClick={async (e)=>{
        e.currentTarget.blur();
        setPending(true);
        try {
          // Map HK
          if (hk === 'CLEAN') {
            const list = await api.listHousekeepingTasks({ tenant, room_id: Number(r.id), status: 'IN_PROGRESS' });
            const task = Array.isArray(list) ? list[0] : null;
            if (task) {
              await api.completeHousekeepingTask({ tenant, id: Number(task.id) });
              addToast && addToast({ id:String(Date.now()), kind:'success', msg:'Housekeeping completed' });
            } else {
              await api.updateRoom({ tenant, id: Number(r.id), housekeeping_status: 'CLEAN' });
              addToast && addToast({ id:String(Date.now()), kind:'info', msg:'Marked CLEAN' });
            }
          } else if (hk === 'IN_PROGRESS') {
            await api.updateRoom({ tenant, id: Number(r.id), housekeeping_status: 'CLEANING' });
            addToast && addToast({ id:String(Date.now()), kind:'success', msg:'Housekeeping in progress' });
          } else {
            await api.updateRoom({ tenant, id: Number(r.id), housekeeping_status: 'DIRTY' });
            addToast && addToast({ id:String(Date.now()), kind:'info', msg:'Marked DIRTY' });
          }
          onUpdated && onUpdated();
        } finally { setPending(false); }
      }}>
        {pending ? 'Updating…' : 'Update'} (U)
      </button>
    </div>
  );
}

function RoomStateButtons({ r, onUpdated }: { r: any; onUpdated?: ()=>void }) {
  const { tenant } = useAppStore();
  const [busy, setBusy] = useState(false);
  const canCheckIn = Number(r.booked_now || 0) === 1 && String(r.status || '').toUpperCase() === 'RESERVED' && Number(r.current_booking_id || 0) > 0;
  const canCheckOut = Number(r.booked_now || 0) === 1 && String(r.status || '').toUpperCase() === 'OCCUPIED' && Number(r.current_booking_id || 0) > 0;
  const canCompleteHK = String(r.status || '').toUpperCase() === 'CLEANING';
  return (
    <div style={{ display:'flex', gap:6, marginTop:8, flexWrap:'wrap' }}>
      {canCheckIn && (
        <button disabled={busy} onClick={async ()=>{ setBusy(true); try { await api.checkInBooking({ tenant, id: Number(r.current_booking_id) }); } finally { setBusy(false); onUpdated && onUpdated(); } }}>Check-in</button>
      )}
      {canCheckOut && (
        <button disabled={busy} onClick={async ()=>{ setBusy(true); try { await api.checkOutBooking({ tenant, id: Number(r.current_booking_id) }); } finally { setBusy(false); onUpdated && onUpdated(); } }}>Check-out</button>
      )}
      {canCompleteHK && (
        <button disabled={busy} onClick={async ()=>{ setBusy(true); try {
          const list = await api.listHousekeepingTasks({ tenant, room_id: Number(r.id), status: 'IN_PROGRESS' });
          const task = Array.isArray(list) ? list[0] : null;
          if (task) await api.completeHousekeepingTask({ tenant, id: Number(task.id) });
        } finally { setBusy(false); onUpdated && onUpdated(); } }}>Complete HK</button>
      )}
    </div>
  );
}

// Utils
function localNowInput() {
  const d = new Date();
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
  return d.toISOString().slice(0,16);
}
function durationMinutes(label: string): number {
  const v = (label||'').toLowerCase();
  if (v==='15m') return 15; if (v==='30m') return 30; if (v==='1h') return 60; if (v==='2h') return 120; if (v==='overnight') return 12*60;
  if (v.includes('1 hour')) return 60; if (v.includes('2 hours')) return 120; if (v.includes('half')) return 240; if (v.includes('full')) return 480; if (v.includes('night')) return 12*60; return 60;
}
function computeEndISO(startLocal: string, dur: string): string | null {
  try { const s = new Date(startLocal); const m = durationMinutes(dur); const e = new Date(s.getTime() + m*60000); return e.toISOString(); } catch { return null; }
}
function previewAmountLabel(room?: Room, dur?: string): string {
  try {
    const rate = Number(room?.base_rate || 0);
    const hours = Math.max(0, durationMinutes(dur||'')/60);
    const rounded = Math.round(hours*2)/2; const amt = Math.round(rate*rounded*100)/100;
    return amt>0 ? `Auto: R ${amt}` : 'Amount (ZAR)';
  } catch { return 'Amount (ZAR)'; }
}
function canonicalDuration(label: string): string {
  switch ((label || '').toLowerCase()) {
    case '1 hour': return '1h';
    case '2 hours': return '2h';
    case '3 hours': return '3h';
    case 'half day': return '4h';
    case 'full day': return '8h';
    case 'night': return '12h';
    default: return '1h';
  }
}
function safeNum(n: any): number { const v = Number(n); return Number.isFinite(v) ? v : 0; }
function safeDate(s?: string) { try { return new Date(String(s)).toLocaleString(); } catch { return String(s || ''); } }

