import React, { useEffect, useState } from "react";
import { api, GuestNote } from "../lib/api";

export default function GuestNotesPage() {
  const [rows, setRows] = useState<GuestNote[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    const ac = new AbortController();
    api.guestNotes(ac.signal).then(setRows).catch(e => setErr(e.message));
    return () => ac.abort();
  }, []);

  return (
    <section>
      <h2 className="text-xl font-semibold mb-3">Guest Notes</h2>
      {err && <div className="mb-3 text-sm text-red-600">Error: {err}</div>}
      <ul className="space-y-2">
        {rows.map(r => (
          <li key={r.id} className="rounded-xl border border-slate-200 p-3 dark:border-slate-800">
            <div className="flex items-center justify-between">
              <div className="font-medium">{r.guest_name}</div>
              <div className="text-xs text-slate-400">{new Date(r.created_at).toLocaleString()}</div>
            </div>
            <div className="text-sm text-slate-700 dark:text-slate-200 mt-1">{r.note}</div>
          </li>
        ))}
        {!rows.length && <li className="text-sm text-slate-500">No guest notes yet.</li>}
      </ul>
    </section>
  );
}
