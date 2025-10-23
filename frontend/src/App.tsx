// src/App.tsx
import { NavLink, Route, Routes } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import HandoverTable from "./components/HandoverTable";
import GuestNotes from "./components/GuestNotes";
import Incidents from "./components/Incidents";
import Pagination from "./components/Pagination";
import TenantSwitcher from "./components/TenantSwitcher";
import CommandPalette from "./components/CommandPalette";
import { useAppStore } from "./store";

export default function App() {
  const { range, setRange, refreshSec, setRefresh } = useAppStore();

  return (
    <div className="wrap">
      <CommandPalette />

      <header className="header card">
        <div className="row">
          <div className="brand">Legacy Skye <span className="muted">Steward</span></div>
          <div className="grow" />
          <nav className="nav">
            <NavLink to="/" end className={({isActive}) => isActive ? "active" : ""}>Dashboard</NavLink>
            <NavLink to="/handovers" className={({isActive}) => isActive ? "active" : ""}>Handovers</NavLink>
            <NavLink to="/notes" className={({isActive}) => isActive ? "active" : ""}>Notes</NavLink>
          </nav>
        </div>

        <div className="row sm-gap">
          <TenantSwitcher />
          <label className="control">
            <span className="label">Range</span>
            <select value={range} onChange={(e) => setRange(e.target.value as any)}>
              <option value="7d">Last 7 days</option>
              <option value="14d">Last 14 days</option>
              <option value="30d">Last 30 days</option>
            </select>
          </label>
          <label className="control">
            <span className="label">Auto-refresh</span>
            <select value={refreshSec} onChange={(e) => setRefresh(Number(e.target.value))}>
              <option value={15}>15s</option>
              <option value={30}>30s</option>
              <option value={60}>60s</option>
            </select>
          </label>
        </div>
      </header>

      <main className="main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route
            path="/handovers"
            element={
              <div className="card">
                <h3 className="card-title">Handovers</h3>
                <HandoverTable />
                <Pagination />
              </div>
            }
          />
          <Route
            path="/notes"
            element={
              <div className="grid-2">
                <div className="card">
                  <h3 className="card-title">Guest Notes</h3>
                  <GuestNotes />
                </div>
                <div className="card">
                  <h3 className="card-title">Incidents</h3>
                  <Incidents />
                </div>
              </div>
            }
          />
        </Routes>
      </main>

      <footer className="footer card">
        <span>© 2025 Legacy Skye • Steward</span>
      </footer>
    </div>
  );
}
