import React, { useEffect, useMemo, useState } from "react";
import { api, Incident } from "../lib/api";

export default function IncidentsPage() {
  const [rows, setRows] = useState<Incident[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    const ac = new AbortController();
    api.incidents(ac.signal).then(setRows).catch(e => setErr(e.message));
    return () => ac.abort();
  }, []);

  const openCount = useMemo(() => rows.filter(r => (r.status ?? "").toLowerCase() !== "resolved").length, [rows]);

  return (
    <section>
      <h2 className="text-xl font-semibold mb-1">Incidents</h2>
      <div className="text-sm text-slate-500 mb-3">Open: {openCount} / Total: {rows.length}</div>
      {err && <div className="mb-3 text-sm text-red-600">Error: {err}</div>}
      <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50 dark:bg-slate-900/40">
            <tr>
              <th className="p-2 text-left">Title</th>
              <th className="p-2 text-left">Area</th>
              <th className="p-2 text-left">Owner</th>
              <th className="p-2 text-left">Status</th>
              <th className="p-2 text-left">Severity</th>
              <th className="p-2 text-left">Due</th>
              <th className="p-2 text-left">Created</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(x => (
              <tr key={x.id} className="border-t border-slate-100 dark:border-slate-800">
                <td className="p-2">{x.title}</td>
                <td className="p-2">{x.area}</td>
                <td className="p-2">{x.owner}</td>
                <td className="p-2">{x.status}</td>
                <td className="p-2">{x.severity}</td>
                <td className="p-2">{x.due_date ? new Date(x.due_date).toLocaleDateString() : "—"}</td>
                <td className="p-2">{new Date(x.created_at).toLocaleString()}</td>
              </tr>
            ))}
            {!rows.length && <tr><td className="p-3 text-slate-500" colSpan={7}>No incidents yet.</td></tr>}
          </tbody>
        </table>
      </div>
    </section>
  );
}
