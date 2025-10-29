// feat(shell): clean sticky header, tabs, controls, logout button; remove duplicate blocks
import React, { useEffect, useMemo, useState } from "react";
import { useAppStore } from "../store";
import { useAuth } from "../auth";
import Select from "../atom/Select";
import UploadWizard from "./UploadWizard";
import { api } from "../api";

type TabKey =
  | "dashboard"
  | "handovers"
  | "incidents"
  | "checklists"
  | "spa"
  | "fleet"
  | "rooms"
  | "concierge"
  | "reports"
  | "notes"
  | "settings";

export default function Shell({ tab, onTabChange, children }: { tab: TabKey; onTabChange: (t: TabKey) => void; children: React.ReactNode }) {
  const { user, logout } = useAuth();
  const { tenant, setTenant, range, setRange, refreshSec, setRefresh, tick } = useAppStore();
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [uploading, setUploading] = useState(false);
  const [wizardOpen, setWizardOpen] = useState(false);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [seeding, setSeeding] = useState(false);

  useEffect(() => { setLastUpdated(new Date()); }, [tick]);

  type TenantLink = { id?: number; name?: string; slug?: string; role?: "owner" | "manager" | "staff" | "viewer" };
  const tenantOptions = useMemo(() => {
    const links: TenantLink[] = (user?.tenants as unknown as TenantLink[]) || [];
    if (Array.isArray(links) && links.length > 0) {
      return links.map((t) => ({ label: (t.name ?? String(t.id)) as string, value: (t.slug || String(t.id ?? t.name)) as string }));
    }
    return [{ label: tenant || "legacy", value: tenant || "legacy" }];
  }, [user, tenant]);

  const activeRole: "owner" | "manager" | "staff" | "viewer" | undefined = useMemo(() => {
    const links: TenantLink[] | undefined = (user?.tenants as unknown as TenantLink[]) || [];
    if (!links) return undefined;
    const match = links.find((t) => t.slug === tenant || String(t.id) === tenant || t.name === tenant);
    return match?.role || undefined;
  }, [user, tenant]);

  const tabs: { k: TabKey; t: string }[] = [
    { k: "dashboard", t: "Dashboard" },
    { k: "handovers", t: "Handovers" },
    { k: "incidents", t: "Incidents" },
    { k: "checklists", t: "Checklists" },
    { k: "spa", t: "Spa" },
    { k: "fleet", t: "Fleet" },
    { k: "rooms", t: "Rooms" },
    { k: "concierge", t: "Concierge" },
    { k: "reports", t: "Reports" },
    { k: "notes", t: "Notes" },
  ];
  if (activeRole && (activeRole === "owner" || activeRole === "manager")) tabs.push({ k: "settings", t: "Settings" });

  const rangeOptions = [
    { label: "Last 7 days", value: "7d" as const },
    { label: "Last 14 days", value: "14d" as const },
    { label: "Last 30 days", value: "30d" as const },
  ];
  const refreshOptions = [
    { label: "15s", value: 15 },
    { label: "30s", value: 30 },
    { label: "60s", value: 60 },
  ];

  return (
    <div className="app">
      <header className="topbar sticky" aria-label="App header with navigation and controls">
        <div className="brand"><strong>Legacy Skye</strong> <span className="muted">Steward</span></div>
        <nav className="tabs" aria-label="Primary">
          {tabs.map(({ k, t }) => (
            <button key={k} className={tab === k ? "active" : ""} onClick={() => onTabChange(k)} aria-current={tab === k ? "page" : undefined}>{t}</button>
          ))}
        </nav>
        <div className="header-controls" aria-label="Account controls" style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span className="muted" style={{ fontSize: 12 }}>{user?.email || ""}</span>
          <button onClick={logout} aria-label="Logout">Logout</button>
        </div>
      </header>

      <div className="container" style={{ paddingTop: 12 }}>
        <div className="controls" role="region" aria-label="Dashboard controls" style={{ marginBottom: 14 }}>
          <div className="control" style={{ minWidth: 220 }}>
            <span className="label">Tenant</span>
            <Select id="ctrl-tenant" label={undefined} options={tenantOptions} value={(tenantOptions.find(o=>o.value===tenant)?.value ?? tenantOptions[0].value)} onChange={(v)=>setTenant(String(v))} />
          </div>
          <div className="control" style={{ minWidth: 200 }}>
            <span className="label">Range</span>
            <Select id="ctrl-range" label={undefined} options={rangeOptions} value={range} onChange={(v)=>setRange(v as "7d" | "14d" | "30d")} />
          </div>
          <div className="control" style={{ minWidth: 140 }}>
            <span className="label">Auto-refresh</span>
            <Select id="ctrl-refresh" label={undefined} options={refreshOptions} value={refreshSec} onChange={(v)=>setRefresh(Number(v))} />
          </div>
          <div className="control" aria-live="polite" aria-atomic="true">
            <span className="label">Last updated</span>
            <span className="muted">{fmtTime(lastUpdated)}</span>
          </div>
          <div className="control">
            <span className="label">Shortcuts</span>
            <span className="muted">/ focus • Cmd/Ctrl+K palette</span>
          </div>
          {(activeRole === "owner" || activeRole === "manager") && (
            <div className="control" style={{ marginLeft: "auto" }}>
              <label htmlFor="upload-sales" className="label" style={{ position: "absolute", left: -10000 }}>Upload Sales CSV</label>
              <input id="upload-sales" type="file" accept=".csv" style={{ display: "none" }} onChange={async (e) => {
                const f = e.target.files?.[0];
                if (!f) return;
                setPendingFile(f);
                setWizardOpen(true);
                (e.target as HTMLInputElement).value = "";
              }} />
              <button className="primary" onClick={() => document.getElementById("upload-sales")?.click()} aria-label="Upload sales CSV" disabled={uploading}>
                {uploading ? "Uploading..." : "Upload sales CSV"}
              </button>
              <button onClick={async ()=>{ setSeeding(true); try { await api.adminSeedAll({ tenant, days: 60 }); } finally { setSeeding(false); } }} disabled={seeding} aria-label="Seed demo data" style={{ marginLeft: 8 }}>
                {seeding ? "Seeding..." : "Seed demo data"}
              </button>
            </div>
          )}
        </div>

        {children}
      </div>
      <UploadWizard
        open={wizardOpen}
        file={pendingFile}
        onClose={()=>{ setWizardOpen(false); setPendingFile(null); }}
        onConfirm={async (file, mapping)=>{ setUploading(true); try { await api.uploadSales({ tenant, file, mapping }); } finally { setUploading(false); } }}
      />
    </div>
  );
}

function fmtTime(d: Date) {
  try {
    return new Intl.DateTimeFormat("en-ZA", {
      hour: "2-digit", minute: "2-digit", second: "2-digit",
      day: "2-digit", month: "2-digit", year: "numeric",
      hour12: true,
      timeZone: "Africa/Johannesburg",
    }).format(d);
  } catch {
    return d.toLocaleString();
  }
}

