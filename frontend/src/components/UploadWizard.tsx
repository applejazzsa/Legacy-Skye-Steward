import React, { useEffect, useMemo, useState } from "react";
import Modal from "./Modal";

type Mapping = {
  date?: string;
  name?: string;
  category?: string;
  qty?: string;
  unit_price?: string;
  sku?: string;
  external_ref?: string;
};

type Props = {
  open: boolean;
  file: File | null;
  onClose: () => void;
  onConfirm: (file: File, mapping: Mapping) => Promise<void>;
};

type Preview = { headers: string[]; rows: Record<string, string>[] };

export default function UploadWizard({ open, file, onClose, onConfirm }: Props) {
  const [preview, setPreview] = useState<Preview | null>(null);
  const [mapping, setMapping] = useState<Mapping>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open || !file) { setPreview(null); setMapping({}); setError(null); return; }
    let alive = true;
    const reader = new FileReader();
    reader.onload = () => {
      if (!alive) return;
      try {
        const text = String(reader.result || "");
        const p = parseCsvPreview(text, 50);
        setPreview(p);
        // auto-map if exact headers present
        const lower = p.headers.map(h => h.toLowerCase());
        const mm: Mapping = {};
        ["date","name","category","qty","unit_price","sku","external_ref"].forEach((k) => {
          const i = lower.indexOf(k);
          if (i >= 0) mm[k as keyof Mapping] = p.headers[i];
        });
        setMapping(mm);
      } catch (err: unknown) {
        const msg = typeof err === 'object' && err && 'message' in err ? String((err as any).message) : 'Failed to parse CSV';
        setError(msg);
      }
    };
    reader.onerror = () => { if (alive) setError("Failed to read file"); };
    reader.readAsText(file);
    return () => { alive = false; };
  }, [open, file]);

  const canConfirm = useMemo(() => {
    if (!file || !preview) return false;
    const req: (keyof Mapping)[] = ["date","name","category","qty","unit_price"];
    return req.every(k => !!mapping[k]);
  }, [file, preview, mapping]);

  return (
    <Modal open={open} title="Upload Sales (CSV)" onClose={onClose}>
      <div className="form-grid">
        <div className="field">
          <label>File</label>
          <div className="muted">{file ? file.name : "No file selected"}</div>
        </div>
        <div className="field">
          <label>Preset</label>
          <select aria-label="Mapping preset" onChange={(e)=>applyPreset(e.target.value, preview, setMapping)} defaultValue="">
            <option value="">Select preset…</option>
            <option value="canonical">Canonical (date,name,category,qty,unit_price)</option>
            <option value="poslite">POS Lite (timestamp,item,cat,quantity,price)</option>
          </select>
        </div>
        <div className="field">
          <label>Template</label>
          <button onClick={downloadTemplate} aria-label="Download sales CSV template">Download CSV Template</button>
        </div>
      </div>
      {error && <div style={{ color: '#ef4444', marginTop: 8 }}>{error}</div>}
      {preview && (
        <div style={{ marginTop: 12 }}>
          <h3>Map Columns</h3>
          <div className="form-grid" style={{ marginTop: 8 }}>
            {renderSelect("Date", "date", preview.headers, mapping, setMapping, true)}
            {renderSelect("Name", "name", preview.headers, mapping, setMapping, true)}
            {renderSelect("Category", "category", preview.headers, mapping, setMapping, true)}
            {renderSelect("Quantity", "qty", preview.headers, mapping, setMapping, true)}
            {renderSelect("Unit Price", "unit_price", preview.headers, mapping, setMapping, true)}
            {renderSelect("SKU (optional)", "sku", preview.headers, mapping, setMapping, false)}
            {renderSelect("External Ref (optional)", "external_ref", preview.headers, mapping, setMapping, false)}
          </div>

          <h3 style={{ marginTop: 12 }}>Preview (first {preview.rows.length} rows)</h3>
          <div style={{ maxHeight: 220, overflow: 'auto', border: '1px solid var(--line)', borderRadius: 10 }}>
            <table className="table" aria-label="Preview table">
              <thead>
                <tr>
                  {preview.headers.map(h => <th key={h}>{h}</th>)}
                </tr>
              </thead>
              <tbody>
                {preview.rows.map((r, idx) => (
                  <tr key={idx}>
                    {preview.headers.map(h => <td key={h}>{String(r[h] ?? "")}</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div style={{ display: 'flex', gap: 8, marginTop: 12, justifyContent: 'flex-end' }}>
        <button onClick={onClose}>Cancel</button>
        <button className="primary" disabled={!canConfirm || busy} onClick={async ()=>{
          if (!file) return;
          setBusy(true);
          try {
            await onConfirm(file, mapping);
            onClose();
          } finally {
            setBusy(false);
          }
        }}>{busy ? 'Processing…' : 'Process'}</button>
      </div>
    </Modal>
  );
}

function renderSelect(
  label: string,
  keyName: keyof Mapping,
  headers: string[],
  mapping: Mapping,
  setMapping: React.Dispatch<React.SetStateAction<Mapping>>,
  required: boolean
) {
  return (
    <div className="field" key={keyName as string}>
      <label>{label}{required ? '' : ' (optional)'}</label>
      <select
        value={(mapping[keyName] as string) || ""}
        onChange={(e) => setMapping(prev => ({ ...prev, [keyName]: e.target.value || undefined }))}
        aria-label={label}
      >
        <option value="">—</option>
        {headers.map(h => <option key={h} value={h}>{h}</option>)}
      </select>
    </div>
  );
}

function parseCsvPreview(text: string, maxRows: number): Preview {
  const lines = text.split(/\r?\n/).filter(l => l.trim().length > 0);
  if (lines.length === 0) throw new Error("Empty CSV");
  const headerCells = parseCsvLine(lines[0]);
  const headers = headerCells.map(normalizeHeader);
  const rows: Record<string, string>[] = [];
  for (let i = 1; i < lines.length && rows.length < maxRows; i++) {
    const cells = parseCsvLine(lines[i]);
    const row: Record<string, string> = {};
    for (let j = 0; j < headers.length; j++) {
      row[headers[j]] = cells[j] ?? "";
    }
    rows.push(row);
  }
  return { headers, rows };
}

function parseCsvLine(line: string): string[] {
  const out: string[] = [];
  let i = 0;
  const n = line.length;
  while (i < n) {
    let c = line[i];
    if (c === '"') {
      // quoted cell
      i++; // skip opening quote
      let buf = '';
      while (i < n) {
        const ch = line[i];
        if (ch === '"') {
          if (i + 1 < n && line[i + 1] === '"') { buf += '"'; i += 2; continue; }
          i++; break; // end quote
        }
        buf += ch; i++;
      }
      out.push(buf);
      if (line[i] === ',') i++;
    } else {
      // unquoted
      let j = i;
      while (j < n && line[j] !== ',') j++;
      out.push(line.slice(i, j));
      i = j + 1;
    }
  }
  return out;
}

function normalizeHeader(h: string): string {
  // Trim and keep original header casing for mapping uniqueness
  return String(h || '').trim();
}

function applyPreset(name: string, preview: Preview | null, setMapping: React.Dispatch<React.SetStateAction<Mapping>>) {
  if (!preview) return;
  const H = preview.headers;
  const lower = (s: string) => s.toLowerCase();
  const find = (...candidates: string[]) => {
    for (const c of candidates) {
      const i = H.findIndex(h => lower(h) === lower(c));
      if (i >= 0) return H[i];
    }
    return undefined;
  };
  if (name === 'canonical') {
    setMapping({
      date: find('date'),
      name: find('name'),
      category: find('category'),
      qty: find('qty'),
      unit_price: find('unit_price'),
      sku: find('sku'),
      external_ref: find('external_ref'),
    });
  } else if (name === 'poslite') {
    setMapping({
      date: find('timestamp', 'date'),
      name: find('item', 'name', 'product'),
      category: find('cat', 'category', 'type'),
      qty: find('quantity', 'qty', 'units'),
      unit_price: find('price', 'unit_price', 'unitprice', 'rate'),
      sku: find('sku', 'code'),
      external_ref: find('external_ref', 'ref', 'order_id'),
    });
  }
}

async function downloadTemplate() {
  try {
    const r = await fetch(`/api/uploads/template/sales.csv`, { credentials: 'include' });
    const text = await r.text();
    const blob = new Blob(["\uFEFF" + text], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sales_template.csv';
    a.click();
    URL.revokeObjectURL(url);
  } catch {
    // silent fail: template is optional helper
  }
}
