import { useState } from "react";
import Dashboard from "./components/Dashboard";
import Handovers from "./components/handovers";
import Notes from "./components/notes";
import Incidents from "./components/Incidents";
import Checklists from "./components/Checklists";
import Fleet from "./components/Fleet";
import Rooms from "./components/Rooms";
import Spa from "./components/Spa";
import Reports from "./components/Reports";
import Settings from "./components/Settings";
import Concierge from "./components/Concierge";
import Login from "./components/Login";
import { useAuth } from "./auth";
import Shell from "./components/Shell";

export default function App() {
  const { user, loading } = useAuth();
  const [tab, setTab] = useState<
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
    | "settings"
  >("dashboard");

  if (loading) {
    return (
      <div className="container">
        <div className="card"><div className="muted">Loading session...</div></div>
      </div>
    );
  }
  if (!user) {
    return <Login />;
  }

  return (
    <Shell tab={tab} onTabChange={setTab}>
      {tab === "dashboard" && <Dashboard />}
      {tab === "handovers" && <Handovers />}
      {tab === "incidents" && <Incidents />}
      {tab === "checklists" && <Checklists />}
      {tab === "spa" && <Spa />}
      {tab === "fleet" && <Fleet />}
      {tab === "rooms" && <Rooms />}
      {tab === "concierge" && <Concierge />}
      {tab === "reports" && <Reports />}
      {tab === "notes" && <Notes />}
      {tab === "settings" && <Settings />}
    </Shell>
  );
}

