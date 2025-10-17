export type JsonMap = Record<string, unknown>

const mode = (import.meta.env.VITE_API_MODE || 'live').toString()
const tenant = (import.meta.env.VITE_TENANT || 'legacy').toString()
const externalBase = (import.meta.env.VITE_API_BASE || '').toString()

// If a relative URL is used and Vite proxy is configured, calls go to /api/... via proxy.
// If an absolute URL is provided, we call it directly (no proxy).
function buildUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) return path
  if (externalBase && !path.startsWith('/api')) {
    // allow passing endpoints like 'api/...' without leading slash
    return `${externalBase}/${path.replace(/^\/?/, '')}`
  }
  return path // relative; let Vite proxy handle /api/...
}

export async function fetchJson<T = JsonMap>(path: string, timeoutMs = 10000): Promise<T> {
  const url = buildUrl(path)
  const ctrl = new AbortController()
  const t = setTimeout(() => ctrl.abort(), timeoutMs)
  try {
    if (mode === 'mock') {
      // In mock mode, load local mock files (e.g., /mock/*.json)
      const res = await fetch(path.startsWith('/mock') ? path : `/mock${path}`, { signal: ctrl.signal })
      if (!res.ok) throw new Error(`Mock HTTP ${res.status} on ${path}`)
      return (await res.json()) as T
    }

    const res = await fetch(url, {
      signal: ctrl.signal,
      headers: { 'X-Tenant': tenant },
    })
    if (!res.ok) {
      const text = await res.text().catch(() => '')
      throw new Error(`HTTP ${res.status} ${res.statusText} for ${url} :: ${text}`)
    }
    return (await res.json()) as T
  } finally {
    clearTimeout(t)
  }
}
