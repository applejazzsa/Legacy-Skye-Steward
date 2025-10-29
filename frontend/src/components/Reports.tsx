// feat(reports): consolidate file, remove duplicates, clean mailto subject
import { useMemo } from "react";
import { useAppStore, makeRange } from "../store";
import { fetchDashboard } from "../api";

export default function Reports() {
  const { tenant, range } = useAppStore();
  const { date_from, date_to } = useMemo(() => makeRange(range), [range]);

  async function exportCSV(scope: "daily" | "weekly") {
    const df = scope === "daily" ? date_from : date_from;
    const dt = scope === "daily" ? date_from : date_to;
    const data = await fetchDashboard(tenant, df, dt, 0);
    const rows: string[] = ["date,total,food,beverage"]; // minimal example
    (data.trend || []).forEach((p) => rows.push(`${(p as any).date},${(p as any).value || (p as any).total || 0},,,`));
    const blob = new Blob([rows.join("\n")], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `report_${scope}_${tenant}_${df}_${dt}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function mailto(scope: "daily" | "weekly") {
    const subject = encodeURIComponent(`Report ${scope} ${tenant} ${date_from}-${date_to}`);
    const body = encodeURIComponent(`Please find the ${scope} summary for ${tenant}.\nRange: ${date_from} to ${date_to}.`);
    window.location.href = `mailto:?subject=${subject}&body=${body}`;
  }

  return (
    <div className="card">
      <h3>Reports & Exports</h3>
      <div className="muted">Daily/weekly CSV export and quick email link.</div>
      <div style={{ display: "flex", gap: 8, marginTop: 8, flexWrap: "wrap" }}>
        <button className="primary" onClick={() => exportCSV("daily")}>
          Export Daily CSV
        </button>
        <button onClick={() => mailto("daily")}>Email Daily</button>
        <button className="primary" onClick={() => exportCSV("weekly")}>
          Export Weekly CSV
        </button>
        <button onClick={() => mailto("weekly")}>Email Weekly</button>
      </div>
    </div>
  );
}

