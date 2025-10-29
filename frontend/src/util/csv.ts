// frontend/src/util/csv.ts
export type CsvRow = Record<string, string | number | null | undefined>;

function escapeCell(v: unknown): string {
  if (v === null || v === undefined) return "";
  const s = String(v);
  // Quote if contains comma, quote, or newline
  if (/[",\n]/.test(s)) {
    return `"${s.replace(/"/g, '""')}"`;
  }
  return s;
}

export function downloadCsv(filename: string, rows: CsvRow[], headerOrder?: string[]) {
  if (!rows || rows.length === 0) {
    // empty file with BOM so Excel opens it properly
    const blob = new Blob(["\uFEFF"], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename.endsWith(".csv") ? filename : `${filename}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    return;
  }

  const headers = headerOrder && headerOrder.length
    ? headerOrder
    : Array.from(new Set(rows.flatMap(r => Object.keys(r || {}))));

  const data = [
    headers.join(","),
    ...rows.map(r => headers.map(h => escapeCell(r?.[h])).join(",")),
  ].join("\n");

  const blob = new Blob(["\uFEFF" + data], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename.endsWith(".csv") ? filename : `${filename}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}
