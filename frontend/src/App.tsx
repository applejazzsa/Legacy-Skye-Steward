import { useEffect, useState } from 'react'
import { fetchJson } from './lib/api'

type KpiSummary = {
  total_covers_7d?: number
  totalCovers7d?: number
  revenue_7d?: number
  revenue7d?: number
  incidents_open?: number
  incidentsOpen?: number
  top_seller?: { name?: string; item?: string; qty?: number } | null
  topSeller?: { name?: string; item?: string; qty?: number } | null
  target?: number
}

type IncidentsResp = {
  total: number
  items: { id: number; outlet: string; severity: string; title: string; status: string }[]
}

type HandoverResp = {
  total: number
  items: { id: number; date: string; outlet: string; shift: string; covers: number }[]
}

type TopItemsResp = {
  items: { name: string; qty: number }[]
}

export default function App() {
  const [kpi, setKpi] = useState<KpiSummary | null>(null)
  const [incidents, setIncidents] = useState<IncidentsResp | null>(null)
  const [handover, setHandover] = useState<HandoverResp | null>(null)
  const [top, setTop] = useState<TopItemsResp | null>(null)
  const [error, setError] = useState<string | null>(null)
  const mode = (import.meta.env.VITE_API_MODE || 'live').toString()
  const tenant = (import.meta.env.VITE_TENANT || 'legacy').toString()

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        setError(null)
        const [k, i, h, t] = await Promise.all([
          fetchJson<KpiSummary>('/api/analytics/kpi-summary?target=10000'),
          fetchJson<IncidentsResp>('/api/incidents'),
          fetchJson<HandoverResp>('/api/handover'),
          fetchJson<TopItemsResp>('/api/analytics/top-items?limit=5'),
        ])
        if (!cancelled) {
          setKpi(k)
          setIncidents(i)
          setHandover(h)
          setTop(t)
        }
      } catch (e: any) {
        if (!cancelled) setError(e?.message ?? String(e))
        // also show something on screen
      }
    }
    load()
    return () => { cancelled = true }
  }, [mode, tenant])

  const covers = kpi?.total_covers_7d ?? kpi?.totalCovers7d ?? 0
  const revenue = kpi?.revenue_7d ?? kpi?.revenue7d ?? 0
  const incidentsOpen = kpi?.incidents_open ?? kpi?.incidentsOpen ?? 0
  const topSeller = kpi?.top_seller ?? kpi?.topSeller ?? null

  return (
    <div style={{ fontFamily: 'ui-sans-serif, system-ui', padding: 24, background: '#0b1020', minHeight: '100vh', color: '#E5E7EB' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 16 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700 }}>Legacy Steward — Dashboard</h1>
        <div style={{ opacity: 0.8, fontSize: 14 }}>
          Mode: <b>{mode.toUpperCase()}</b> &nbsp;|&nbsp; Tenant: <b>{tenant}</b>
        </div>
      </header>

      {error ? (
        <div style={{ background: '#1f2937', border: '1px solid #6b7280', padding: 12, borderRadius: 8, marginBottom: 16 }}>
          <div style={{ fontWeight: 600, marginBottom: 6 }}>Error</div>
          <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{error}</pre>
          <div style={{ marginTop: 8, fontSize: 13, opacity: 0.9 }}>
            Check the backend is running at <code>http://127.0.0.1:8000/health</code> and that your <code>.env.local</code> is set.
          </div>
        </div>
      ) : null}

      {/* KPI cards */}
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0,1fr))', gap: 12, marginBottom: 16 }}>
        <KpiCard title="7-Day Covers" value={covers.toLocaleString()} />
        <KpiCard title="7-Day Revenue" value={`R ${Number(revenue).toLocaleString()}`} />
        <KpiCard title="Open Incidents" value={incidentsOpen.toLocaleString()} />
        <KpiCard title="Top Seller" value={topSeller ? `${topSeller.name ?? topSeller.item} (${topSeller.qty})` : '—'} />
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <Panel title="Recent Handovers">
          {!handover ? (
            <Skeleton rows={4} />
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <Th>Date</Th><Th>Outlet</Th><Th>Shift</Th><Th style={{ textAlign: 'right' }}>Covers</Th>
                </tr>
              </thead>
              <tbody>
                {handover.items.map((h) => (
                  <tr key={h.id}>
                    <Td>{h.date}</Td>
                    <Td>{h.outlet}</Td>
                    <Td>{h.shift}</Td>
                    <Td style={{ textAlign: 'right' }}>{h.covers}</Td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Panel>

        <Panel title="Open / In-Progress Incidents">
          {!incidents ? (
            <Skeleton rows={4} />
          ) : incidents.items.length === 0 ? (
            <div style={{ opacity: 0.8 }}>No incidents 🎉</div>
          ) : (
            <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
              {incidents.items.map((i) => (
                <li key={i.id} style={{ padding: '8px 0', borderBottom: '1px solid #293044' }}>
                  <div style={{ fontWeight: 600 }}>{i.title}</div>
                  <div style={{ fontSize: 13, opacity: 0.9 }}>{i.outlet} • {i.severity} • {i.status}</div>
                </li>
              ))}
            </ul>
          )}
        </Panel>
      </div>

      <Panel title="Top Items (7-day)">
        {!top ? (
          <Skeleton rows={4} />
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr><Th>Item</Th><Th style={{ textAlign: 'right' }}>Qty</Th></tr>
            </thead>
            <tbody>
              {top.items.map((r) => (
                <tr key={r.name}>
                  <Td>{r.name}</Td>
                  <Td style={{ textAlign: 'right' }}>{r.qty}</Td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Panel>
    </div>
  )
}

/** Small presentational components */
function KpiCard({ title, value }: { title: string; value: string }) {
  return (
    <div style={{ background: '#0f172a', border: '1px solid #293044', padding: 16, borderRadius: 12 }}>
      <div style={{ fontSize: 13, opacity: 0.8, marginBottom: 6 }}>{title}</div>
      <div style={{ fontSize: 22, fontWeight: 700 }}>{value}</div>
    </div>
  )
}

function Panel({ title, children }: { title: string; children: any }) {
  return (
    <section style={{ background: '#0f172a', border: '1px solid #293044', padding: 16, borderRadius: 12, marginTop: 16 }}>
      <div style={{ fontWeight: 700, marginBottom: 10 }}>{title}</div>
      {children}
    </section>
  )
}

function Th({ children, style }: any) {
  return <th style={{ textAlign: 'left', fontSize: 13, opacity: 0.8, padding: '6px 0', borderBottom: '1px solid #293044', ...style }}>{children}</th>
}
function Td({ children, style }: any) {
  return <td style={{ padding: '8px 0', borderBottom: '1px solid #293044', ...style }}>{children}</td>
}

function Skeleton({ rows = 3 }: { rows?: number }) {
  return (
    <div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} style={{ height: 16, background: '#1b2340', borderRadius: 6, margin: '6px 0' }} />
      ))}
    </div>
  )
}
