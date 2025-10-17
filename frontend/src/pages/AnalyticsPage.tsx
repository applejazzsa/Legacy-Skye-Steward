import React, { useEffect, useState } from "react";
import { api, TopItem } from "../lib/api";

export default function AnalyticsPage() {
  const [items, setItems] = useState<TopItem[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    const ac = new AbortController();
    api.topItems(5, ac.signal).then(setItems).catch(e => setErr(e.message));
    return () => ac.abort();
  }, []);

  return (
    <section>
      <h2 className="text-xl font-semibold mb-3">Top Items (7d)</h2>
      {err && <div className="mb-3 text-sm text-red-600">Error: {err}</div>}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
        {items.map(i => (
          <div key={i.name} className="rounded-xl border border-slate-200 p-3 dark:border-slate-800">
            <div className="text-sm font-semibold">{i.name}</div>
            <div className="text-sm text-slate-500">Orders: {i.count}</div>
          </div>
        ))}
        {!items.length && <div className="text-sm text-slate-500">No data yet.</div>}
      </div>
    </section>
  );
}
