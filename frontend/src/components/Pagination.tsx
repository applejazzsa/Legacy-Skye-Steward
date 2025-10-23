// src/components/Pagination.tsx
import { useEffect, useState } from "react";

export default function Pagination() {
  const [total, setTotal] = useState(0);
  const [pageSize, setPageSize] = useState(8);
  const [page, setPage] = useState(1);

  useEffect(() => {
    const onMeta = (e: Event) => {
      const { total, pageSize } = (e as CustomEvent).detail as { total: number; pageSize: number };
      setTotal(total);
      setPageSize(pageSize);
    };
    window.addEventListener("handover:total", onMeta as EventListener);
    return () => window.removeEventListener("handover:total", onMeta as EventListener);
  }, []);

  const pages = Math.max(1, Math.ceil(total / pageSize));
  useEffect(() => {
    if (page > pages) setPage(pages);
  }, [pages]);

  const go = (p: number) => {
    const clamped = Math.min(Math.max(1, p), pages);
    setPage(clamped);
    window.dispatchEvent(new CustomEvent("handover:setPage", { detail: clamped }));
  };

  if (pages <= 1) return null;

  return (
    <div className="pagination">
      <button onClick={() => go(page - 1)} disabled={page <= 1}>Prev</button>
      <span>Page {page} / {pages}</span>
      <button onClick={() => go(page + 1)} disabled={page >= pages}>Next</button>
    </div>
  );
}
