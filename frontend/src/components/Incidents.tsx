import { useEffect, useState } from "react";
import { useAppStore } from "../store";
import { makeRange, api } from "../api";

type Incident = {
  id: string | number;
  when: string;     // ISO
  severity: "low" | "medium" | "high" | string;
  summary: string;
  reported_by?: string;
};

const MOCK: Incident[] = [
  {
    id: "i1",
    when: new Date().toISOString(),
    severity: "low",
    summary: "Incidents API not found. Showing placeholder incident.",
    reported_by: "System",
  },
];

export default function Incidents() {
  const { tenant, range } = useAppStore();
  const { date_from, date_to } = makeRange(range);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    (async () => {
      setLoading(true);
      try {
        const fn: any = (api as any).incidents;
        if (typeof fn === "function") {
          const data: Incident[] = await fn({ tenant, date_from, date_to });
          if (!alive) return;
          setIncidents(Array.isArray(data) ? data : []);
        } else {
          if (!alive) return;
          setIncidents(MOCK);
        }
      } catch {
        if (!alive) return;
        setIncidents(MOCK);
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, [tenant, range, date_from, date_to]);

  if (loading) return <p className="muted">Loading incidents…</p>;
  if (incidents.length === 0) return <p className="muted">No incidents.</p>;

  return (
    <div style={{ display: "grid", gap: 8 }}>
      {incidents.map((i) => (
        <div key={i.id} className="card" style={{ padding: 10 }}>
          <div style={{ display: "flex", gap: 8, justifyContent: "space-between" }}>
            <strong style={{ textTransform: "capitalize" }}>{i.severity}</strong>
            <span className="muted">{new Date(i.when).toLocaleString()}</span>
          </div>
          <div style={{ marginTop: 6 }}>{i.summary}</div>
          {i.reported_by && (
            <div className="muted" style={{ marginTop: 6 }}>
              Reported by: {i.reported_by}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
