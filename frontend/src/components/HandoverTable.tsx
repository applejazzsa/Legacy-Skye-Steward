// src/components/HandoverTable.tsx
import { useEffect, useState } from "react";
import { api } from "../api";
import { useAppStore } from "../store";

type Handover = {
  id: string;
  shift: "AM" | "PM";
  author: string;
  created_at: string; // ISO
  summary: string;
};

export default function HandoverTable() {
  const { tenant } = useAppStore();
  const [rows, setRows] = useState<Handover[]>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 8;

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        // if you already have an API, use it; otherwise we’ll synthesize
        const res = await api.handoverList?.({ tenant, page, page_size: pageSize });
        if (!alive) return;
        if (res && Array.isArray(res.items)) {
          setRows(res.items);
          setTotal(res.total ?? res.items.length);
        } else {
          // Placeholder dataset to keep the UI alive
          const demo: Handover[] = Array.from({ length: pageSize }, (_, i) => {
            const idx = (page - 1) * pageSize + i + 1;
            return {
              id: `demo-${idx}`,
              shift: i % 2 === 0 ? "AM" : "PM",
              author: i % 2 === 0 ? "System" : "Manager",
              created_at: new Date(Date.now() - i * 3600_000).toISOString(),
              summary:
                i % 2 === 0
                  ? "Sample: FOH ready, no incidents. Inventory checked."
                  : "Sample: Busy lunch, 2 comps. Bar 86% target.",
            };
          });
          setRows(demo);
          setTotal(42);
        }
      } catch {
        if (!alive) return;
        const demo: Handover[] = Array.from({ length: pageSize }, (_, i) => {
          const idx = (page - 1) * pageSize + i + 1;
          return {
            id: `demo-${idx}`,
            shift: i % 2 === 0 ? "AM" : "PM",
            author: i % 2 === 0 ? "System" : "Manager",
            created_at: new Date(Date.now() - i * 3600_000).toISOString(),
            summary:
              i % 2 === 0
                ? "Sample: FOH ready, no incidents. Inventory checked."
                : "Sample: Busy lunch, 2 comps. Bar 86% target.",
          };
        });
        setRows(demo);
        setTotal(42);
      }
    })();
    return () => {
      alive = false;
    };
  }, [tenant, page]);

  // expose page change globally through a custom event the shared Pagination listens for
  useEffect(() => {
    const onPage = (e: Event) => {
      const detail = (e as CustomEvent).detail as number;
      setPage(detail);
    };
    window.addEventListener("handover:setPage", onPage as EventListener);
    return () => window.removeEventListener("handover:setPage", onPage as EventListener);
  }, []);

  // let Pagination know the total (again via event to keep it decoupled)
  useEffect(() => {
    const ev = new CustomEvent("handover:total", { detail: { total, pageSize } });
    window.dispatchEvent(ev);
  }, [total]);

  return (
    <div className="table">
      <div className="thead">
        <div>Date</div>
        <div>Shift</div>
        <div>Author</div>
        <div>Summary</div>
      </div>
      {rows.map((r) => (
        <div className="trow" key={r.id}>
          <div>{new Date(r.created_at).toLocaleString()}</div>
          <div>{r.shift}</div>
          <div>{r.author}</div>
          <div className="ellipsis">{r.summary}</div>
        </div>
      ))}
      {rows.length === 0 && <p className="muted">No handovers.</p>}
    </div>
  );
}
