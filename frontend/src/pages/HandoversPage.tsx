import React, { useEffect, useState } from "react";
import { api, Handover } from "../lib/api";

export default function HandoversPage() {
  const [rows, setRows] = useState<Handover[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    const ac = new AbortController();
    api.handovers(ac.signal).then(setRows).catch(e => setErr(e.message));
    return () => ac.abort();
  }, []);

  return (
    <section>
      <h2 className="text-xl font-semibold mb-3">Handovers</h2>
      {err && <div className="mb-3 text-sm text-red-600">Error: {err}</div>}
      <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50 dark:bg-slate-900/40">
            <tr>
              <th className="text-left p-2">Date</th>
              <th className="text-left p-2">Outlet</th>
              <th className="text-left p-2">Shift</th>
              <th className="text-right p-2">Bookings</th>
              <th className="text-right p-2">Walk-ins</th>
              <th className="text-right p-2">Covers</th>
              <th className="text-right p-2">Food Rev</th>
              <th className="text-right p-2">Beverage Rev</th>
              <th className="text-left p-2">Top Sales</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(h => (
              <tr key={h.id} className="border-t border-slate-100 dark:border-slate-800">
                <td className="p-2">{new Date(h.date).toLocaleString()}</td>
                <td className="p-2">{h.outlet}</td>
                <td className="p-2">{h.shift}</td>
                <td className="p-2 text-right">{h.bookings}</td>
                <td className="p-2 text-right">{h.walk_ins}</td>
                <td className="p-2 text-right">{h.covers}</td>
                <td className="p-2 text-right">£{h.food_revenue.toLocaleString()}</td>
                <td className="p-2 text-right">£{h.beverage_revenue.toLocaleString()}</td>
                <td className="p-2">{h.top_sales}</td>
              </tr>
            ))}
            {!rows.length && <tr><td className="p-3 text-slate-500" colSpan={9}>No data yet.</td></tr>}
          </tbody>
        </table>
      </div>
    </section>
  );
}
