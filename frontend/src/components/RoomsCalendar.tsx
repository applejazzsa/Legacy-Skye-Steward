import { useEffect, useMemo, useRef, useState } from "react";
import { api } from "../api";
import { useAppStore, makeRange } from "../store";

type Room = { id: number; name: string };
type Booking = { id: number; room_id: number; start_at: string; end_at: string; purpose?: string };

export default function RoomsCalendar() {
  const { tenant, range } = useAppStore();
  const [rooms, setRooms] = useState<Room[]>([]);
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [drag, setDrag] = useState<{ room_id: number; start: Date; end?: Date } | null>(null);
  const gridRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    (async () => {
      const rs = await api.listRooms({ tenant });
      setRooms(Array.isArray(rs) ? (rs as Room[]) : []);
      const { date_from, date_to } = makeRange(range);
      const bs = await api.listRoomBookings({ tenant, limit: 200, date_from, date_to });
      setBookings(Array.isArray(bs) ? (bs as Booking[]) : []);
    })();
  }, [tenant, range]);

  const week = useMemo(() => startOfWeek(new Date()), []);
  const endWeek = useMemo(() => new Date(week.getTime() + 7 * 24 * 3600 * 1000), [week]);

  const bars = useMemo(() => {
    const spanMs = endWeek.getTime() - week.getTime();
    return bookings.map((b) => {
      const s = clampDate(new Date(b.start_at), week, endWeek);
      const e = clampDate(new Date(b.end_at), week, endWeek);
      const left = ((s.getTime() - week.getTime()) / spanMs) * 100;
      const width = Math.max(0.5, ((e.getTime() - s.getTime()) / spanMs) * 100);
      return { ...b, left, width };
    });
  }, [bookings, week, endWeek]);

  function onGridDown(room_id: number, e: React.MouseEvent) {
    if (!gridRef.current) return;
    const rect = gridRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const inWeek = x / rect.width; // 0..1
    const ms = week.getTime() + inWeek * (endWeek.getTime() - week.getTime());
    setDrag({ room_id, start: roundTo15(new Date(ms)) });
  }
  function onGridMove(e: React.MouseEvent) {
    if (!drag || !gridRef.current) return;
    const rect = gridRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const inWeek = Math.min(1, Math.max(0, x / rect.width));
    const ms = week.getTime() + inWeek * (endWeek.getTime() - week.getTime());
    setDrag({ ...drag, end: roundTo15(new Date(ms)) });
  }
  async function onGridUp() {
    if (!drag || !drag.end) { setDrag(null); return; }
    const start = drag.start < drag.end ? drag.start : drag.end;
    const end = drag.start < drag.end ? drag.end : drag.start;
    if (end.getTime() - start.getTime() < 30 * 60000) { setDrag(null); return; }
    await api.createRoomBooking({ tenant, room_id: drag.room_id, start: start.toISOString(), end: end.toISOString(), purpose: "Calendar" });
    const { date_from, date_to } = makeRange(range);
    const bs = await api.listRoomBookings({ tenant, limit: 200, date_from, date_to });
    setBookings(Array.isArray(bs) ? (bs as Booking[]) : []);
    setDrag(null);
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-2">
        <h3>Rooms Calendar (Week)</h3>
        <div className="muted">Drag across a lane to create a booking</div>
      </div>
      <div ref={gridRef} onMouseMove={onGridMove} onMouseUp={onGridUp} className="relative border rounded-md overflow-hidden" style={{ height: Math.max(200, rooms.length * 48) }}>
        {/* grid background */}
        <WeekGrid />
        {/* lanes */}
        <div className="absolute inset-0">
          {rooms.map((r, idx) => (
            <div key={r.id} className="absolute left-0 right-0 border-b border-slate-200" style={{ top: idx * 48, height: 48 }} onMouseDown={(e)=>onGridDown(r.id, e)}>
              <div className="absolute left-2 top-2 text-xs text-slate-500">{r.name}</div>
              {/* bookings */}
              {bars.filter(b=>b.room_id===r.id).map(b => (
                <div key={b.id} className="absolute bg-indigo-500/80 text-white text-xs px-2 py-1 rounded" style={{ left: `${b.left}%`, width: `${b.width}%`, top: 20, height: 20, overflow:'hidden', whiteSpace:'nowrap' }}>
                  {b.purpose || 'Booking'}
                </div>
              ))}
            </div>
          ))}
          {/* drag preview */}
          {drag && drag.end && (
            <DragPreview week={week} endWeek={endWeek} start={drag.start} end={drag.end} rooms={rooms} room_id={drag.room_id} />
          )}
        </div>
      </div>
    </div>
  );
}

function WeekGrid() {
  const days = [0,1,2,3,4,5,6];
  return (
    <div className="absolute inset-0 grid" style={{ gridTemplateColumns: 'repeat(7, 1fr)' }}>
      {days.map(i => (
        <div key={i} className="border-r border-slate-200 bg-slate-50/40" />
      ))}
    </div>
  );
}

function DragPreview({ week, endWeek, start, end, rooms, room_id }: { week: Date; endWeek: Date; start: Date; end: Date; rooms: Room[]; room_id: number }) {
  const idx = rooms.findIndex(r=>r.id===room_id);
  const spanMs = endWeek.getTime() - week.getTime();
  const s = start < end ? start : end;
  const e = start < end ? end : start;
  const left = ((s.getTime() - week.getTime()) / spanMs) * 100;
  const width = Math.max(0.5, ((e.getTime() - s.getTime()) / spanMs) * 100);
  return (
    <div className="absolute" style={{ top: idx * 48 + 20, left: `${left}%`, width: `${width}%`, height: 20 }}>
      <div className="bg-emerald-500/80 text-white text-xs px-2 py-1 rounded">New</div>
    </div>
  );
}

function startOfWeek(d: Date) { const dt = new Date(d); const day = dt.getDay(); const diff = (day === 0 ? -6 : 1 - day); dt.setDate(dt.getDate() + diff); dt.setHours(0,0,0,0); return dt; }
function roundTo15(d: Date) { const ms = 15*60000; return new Date(Math.round(d.getTime()/ms)*ms); }
function clampDate(d: Date, a: Date, b: Date) { return new Date(Math.max(a.getTime(), Math.min(b.getTime(), d.getTime()))); }

