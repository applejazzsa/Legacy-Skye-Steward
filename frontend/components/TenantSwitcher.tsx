import { setTenant } from '../lib/api'
import { useEffect, useState } from 'react'

const KNOWN = ['legacy', 'oceanview']

export default function TenantSwitcher() {
  const [tenant, set] = useState<string>(() => {
    try {
      return localStorage.getItem('tenant') || import.meta.env.VITE_TENANT || 'legacy'
    } catch {
      return import.meta.env.VITE_TENANT || 'legacy'
    }
  })

  useEffect(() => {
    // keep localStorage in sync if env changed
    try {
      const stored = localStorage.getItem('tenant')
      if (!stored) localStorage.setItem('tenant', tenant)
    } catch {}
  }, [])

  function onChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const next = e.target.value
    set(next)
    setTenant(next)
    // reload to ensure all queries pick up new header
    window.location.reload()
  }

  return (
    <label style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
      <span style={{ fontSize: 13, opacity: 0.9 }}>Tenant:</span>
      <select value={tenant} onChange={onChange} style={{ padding: '6px 10px', borderRadius: 8, background: '#0f172a', color: '#e5e7eb', border: '1px solid #293044' }}>
        {KNOWN.map(t => <option key={t} value={t}>{t}</option>)}
      </select>
    </label>
  )
}
