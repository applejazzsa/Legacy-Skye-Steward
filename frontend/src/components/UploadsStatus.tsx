import { useEffect, useMemo, useRef, useState } from "react";
import { useAppStore } from "../store";
import { api } from "../api";
import Modal from "./Modal";

type UploadRow = { id: number; filename: string; status: string; rows_total: number; rows_ok: number; rows_failed: number; created_at?: string; completed_at?: string };

export default function UploadsStatus() {
  const { tenant } = useAppStore();
  const [items, setItems] = useState<UploadRow[]>([]);
  const [openId, setOpenId] = useState<number | null>(null);
  const [openLog, setOpenLog] = useState<string | null>(null);
  const timerRef = useRef<number | null>(null);

  const busy = useMemo(() => items.some(i => i.status === "queued" || i.status === "processing"), [items]);

  async function refreshOnce() {
    const res = await api.listUploads({ tenant });
    setItems(res?.items || []);
  }

  useEffect(() => {
    let alive = true;
    (async () => {
      await refreshOnce();
    })();
    return () => { alive = false; };
  }, [tenant]);

  useEffect(() => {
    if (timerRef.current) window.clearInterval(timerRef.current);
    if (busy) {
      timerRef.current = window.setInterval(() => { refreshOnce(); }, 5000) as unknown as number;
    }
    return () => { if (timerRef.current) window.clearInterval(timerRef.current); };
  }, [busy, tenant]);

  return (
    <div className="card" aria-label="Uploads status">
      <h3>Recent Uploads</h3>
      {items.length === 0 ? (
        <p className="muted">No uploads yet.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>File</th>
              <th>Status</th>
              <th>Progress</th>
              <th>Created</th>
              <th>Completed</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {items.map(u => {
              const pct = u.rows_total ? Math.round((u.rows_ok / u.rows_total) * 100) : 0;
              return (
                <tr key={u.id}>
                  <td>{u.filename}</td>
                  <td>{u.status}</td>
                  <td>{u.status === "done" || u.status === "failed" ? `${u.rows_ok}/${u.rows_total}` : `${pct}%`}</td>
                  <td>{u.created_at ? new Date(u.created_at).toLocaleString() : ""}</td>
                  <td>{u.completed_at ? new Date(u.completed_at).toLocaleString() : ""}</td>
                  <td>
                    {(u.status === "failed" || u.status === "done") && (
                      <button onClick={async ()=>{
                        const detail = await api.getUpload({ tenant, id: u.id });
                        const log = detail?.error_log || null;
                        setOpenId(u.id);
                        setOpenLog(log);
                      }}>View errors</button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
      <Modal open={openId !== null} title={`Upload ${openId} Errors`} onClose={()=>{ setOpenId(null); setOpenLog(null); }}>
        {openLog ? (
          <>
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 8 }}>
              <button onClick={()=>downloadErrors(openId!, openLog)} aria-label="Download error log JSON">Download JSON</button>
            </div>
            <pre style={{ whiteSpace: "pre-wrap" }}>{truncateLog(openLog)}</pre>
          </>
        ) : (
          <p className="muted">No errors recorded.</p>
        )}
      </Modal>
    </div>
  );
}

function truncateLog(raw: string) {
  try {
    const arr = JSON.parse(raw);
    if (Array.isArray(arr)) {
      return arr.slice(0, 100).join("\n");
    }
  } catch {}
  return String(raw).slice(0, 4000);
}

function downloadErrors(id: number, raw: string) {
  const blob = new Blob([raw], { type: 'application/json;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `upload_${id}_errors.json`;
  a.click();
  URL.revokeObjectURL(url);
}
