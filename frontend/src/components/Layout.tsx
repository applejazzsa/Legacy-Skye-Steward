import React, { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";

/** ----- Brand Header (top bar) ----- */
function HeaderBar({ onToggleSidebar }: { onToggleSidebar: () => void }) {
  useEffect(() => {
    document.title = "Steward – A Product of Legacy Skye";
  }, []);

  return (
    <header className="sticky top-0 z-40 flex items-center justify-between bg-white/90 backdrop-blur shadow-sm px-4 md:px-6 py-3 border-b border-slate-200">
      <div className="flex items-center gap-3">
        <button
          className="md:hidden inline-flex items-center justify-center rounded-xl border border-slate-200 h-10 w-10"
          aria-label="Toggle menu"
          onClick={onToggleSidebar}
        >
          <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2">
            <path strokeLinecap="round" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        <div className="flex items-center gap-3">
          <img src="/assets/steward-logo.png" alt="Steward logo" className="h-10 w-auto" />
          <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">Steward</h1>
        </div>
      </div>

      <div className="hidden md:block">
        <span className="text-sm font-medium text-slate-500 uppercase tracking-wide">
          A Product of Legacy Skye
        </span>
      </div>

      <div className="flex items-center gap-3">
        <ThemeToggle />
        <img src="/assets/legacy-skye-logo.png" alt="Legacy Skye logo" className="h-8 w-auto" />
      </div>
    </header>
  );
}

/** ----- Sidebar ----- */
function Sidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `group flex w-full items-center justify-between rounded-xl px-3 py-2.5 transition
     ${isActive ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"}`;

  return (
    <>
      <div
        className={`fixed inset-0 z-30 bg-black/30 transition-opacity md:hidden ${open ? "opacity-100" : "pointer-events-none opacity-0"}`}
        onClick={onClose}
      />
      <aside
        className={`fixed z-40 inset-y-0 left-0 w-80 max-w-[85vw] transform transition-transform
        md:static md:translate-x-0 md:w-72
        ${open ? "translate-x-0" : "-translate-x-full"}`}
      >
        <div className="h-full flex flex-col border-r border-slate-200 bg-gradient-to-b from-slate-50 to-white px-4 py-4 dark:from-slate-900 dark:to-slate-950 dark:border-slate-800">
          <div className="mb-3">
            <div className="text-[11px] uppercase tracking-[0.18em] text-slate-500">Product</div>
            <div className="mt-1 text-base font-semibold text-slate-900 dark:text-white">Steward — A Product of Legacy Skye</div>
          </div>

          <nav className="space-y-1.5">
            <NavLink to="/" className={linkClass} end onClick={onClose}>
              <span className="flex items-center gap-2.5"><IconGauge /><span className="text-sm font-medium">Dashboard</span></span>
              <Badge>Live</Badge>
            </NavLink>
            <NavLink to="/handovers" className={linkClass} onClick={onClose}>
              <span className="flex items-center gap-2.5"><IconNotebook /><span className="text-sm font-medium">Handovers</span></span>
            </NavLink>
            <NavLink to="/guest-notes" className={linkClass} onClick={onClose}>
              <span className="flex items-center gap-2.5"><IconChat /><span className="text-sm font-medium">Guest Notes</span></span>
            </NavLink>
            <NavLink to="/incidents" className={linkClass} onClick={onClose}>
              <span className="flex items-center gap-2.5"><IconAlert /><span className="text-sm font-medium">Incidents</span></span>
            </NavLink>
            <NavLink to="/analytics" className={linkClass} onClick={onClose}>
              <span className="flex items-center gap-2.5"><IconChart /><span className="text-sm font-medium">Analytics</span></span>
            </NavLink>
            <div className="pt-2 border-t border-slate-200 mt-2 dark:border-slate-800" />
            <NavLink to="/reports" className={linkClass} onClick={onClose}>
              <span className="flex items-center gap-2.5"><IconReport /><span className="text-sm font-medium">Reports</span></span>
            </NavLink>
            <NavLink to="/settings" className={linkClass} onClick={onClose}>
              <span className="flex items-center gap-2.5"><IconSettings /><span className="text-sm font-medium">Settings</span></span>
            </NavLink>
          </nav>

          <div className="mt-auto pt-4">
            <div className="rounded-xl border border-slate-200 p-3 dark:border-slate-800">
              <div className="text-[11px] uppercase tracking-[0.18em] text-slate-500">Environment</div>
              <div className="mt-1 text-sm font-medium text-slate-900 dark:text-white">Production</div>
              <div className="mt-2 flex gap-2">
                <Badge>v0.1.0</Badge>
                <Badge>Stable</Badge>
              </div>
            </div>
            <div className="text-[11px] text-slate-400 mt-3">
              © {new Date().getFullYear()} Legacy Skye
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}

function ContentShell() {
  return (
    <main className="flex-1 bg-slate-50 dark:bg-slate-950">
      <div className="mx-auto max-w-7xl px-4 md:px-6 py-6">
        <Outlet />
      </div>
    </main>
  );
}

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  return (
    <div className="min-h-screen w-full bg-white text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <HeaderBar onToggleSidebar={() => setSidebarOpen((v) => !v)} />
      <div className="flex">
        <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <ContentShell />
      </div>
    </div>
  );
}

/* ---- small atoms/icons ---- */
function ThemeToggle() {
  const [dark, setDark] = useState(false);
  useEffect(() => {
    const isDark = localStorage.getItem("theme") === "dark" ||
      (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches);
    setDark(isDark);
    document.documentElement.classList.toggle("dark", isDark);
  }, []);
  const toggle = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle("dark", next);
    localStorage.setItem("theme", next ? "dark" : "light");
  };
  return (
    <button
      onClick={toggle}
      className="inline-flex items-center gap-2 rounded-xl border border-slate-200 h-10 px-3 text-sm hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-900"
      aria-label="Toggle theme"
      title="Toggle theme"
    >
      {dark ? <IconMoon /> : <IconSun />}
      <span className="hidden md:inline">{dark ? "Dark" : "Light"}</span>
    </button>
  );
}
function Badge({ children }: { children: React.ReactNode }) {
  return (
    <span className="rounded-lg bg-slate-100 px-2 py-0.5 text-xs text-slate-600 dark:bg-slate-800 dark:text-slate-200">
      {children}
    </span>
  );
}
function IconGauge() { return (<svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path strokeWidth="2" d="M12 3a9 9 0 1 0 9 9M12 3v4" /><path strokeWidth="2" strokeLinecap="round" d="M12 12l4 2" /></svg>); }
function IconNotebook() { return (<svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="5" y="3" width="14" height="18" rx="2" /><path d="M9 7h6M9 11h6M9 15h4" /></svg>); }
function IconChat() { return (<svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a4 4 0 0 1-4 4H7l-4 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z" /></svg>); }
function IconAlert() { return (<svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 9v4M12 17h.01" /><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" /></svg>); }
function IconChart() { return (<svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 3v18h18" /><rect x="7" y="12" width="3" height="6" /><rect x="12" y="9" width="3" height="9" /><rect x="17" y="5" width="3" height="13" /></svg>); }
function IconReport() { return (<svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 3h6l4 4v14a2 2 0 0 1-2 2H9l-4-4V5a2 2 0 0 1 2-2z" /><path d="M9 7h7v4H9z" /></svg>); }
function IconSettings() { return (<svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z" /><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V22a2 2 0 1 1-4 0v-.07a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06A2 2 0 1 1 4.21 17l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.07c.66 0 1.24-.39 1.51-1z" /></svg>); }
function IconSun() { return (<svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="4" strokeWidth="2" /><path strokeWidth="2" d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.4 1.4M17.6 17.6l1.4 1.4M5 19l1.4-1.4M17.6 6.4 19 5" /></svg>); }
function IconMoon() { return (<svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path strokeWidth="2" d="M20 15.5A8.38 8.38 0 0 1 8.5 4 7 7 0 1 0 20 15.5z" /></svg>); }
