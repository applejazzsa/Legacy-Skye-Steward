import ErrorBoundary from "./components/ErrorBoundary";
import KpiSummaryCard from "./components/KpiSummary";
import HandoverTable from "./components/HandoverTable";
import GuestNotes from "./components/GuestNotes";
import TopItems from "./components/TopItems";

export default function App() {
  return (
    <ErrorBoundary>
      <div className="container">
        <div className="header">
          <div className="h1">Skye Steward</div>
          <div className="sub">Operations Dashboard</div>
        </div>

        <div className="grid">
          <div className="stack" style={{display:'grid', gap:16}}>
            <KpiSummaryCard />
            <HandoverTable />
          </div>
          <div className="stack" style={{display:'grid', gap:16}}>
            <TopItems />
            <GuestNotes />
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}
