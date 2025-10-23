export type JsonMap = Record<string, unknown>

const mode = (import.meta.env.VITE_API_MODE || 'live').toString()
const envTenant = (import.meta.env.VITE_TENANT || 'legacy').toString()
const externalBase = (import.meta.env.VITE_API_BASE || '').toString()

// Allow runtime override via localStorage
function getTenant(): string {
  try {
    const ls = localStorage.getItem('tenant')
    return (ls && ls.trim()) || envTenant
  } catch {
    return envTenant
  }
}

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

export async function fetchJson<T = JsonMap>(path: string, timeoutMs = 10000, init?: RequestInit): Promise<T> {
  const url = buildUrl(path)
  const ctrl = new AbortController()
  const timer = setTimeout(() => ctrl.abort(), timeoutMs)
  const tenant = getTenant()

  try {
    if (mode === 'mock') {
      const mockPath = path.startsWith('/mock') ? path : `/mock${path}`
      const res = await fetch(mockPath, { signal: ctrl.signal })
      if (!res.ok) throw new Error(`Mock HTTP ${res.status} on ${mockPath}`)
      return (await res.json()) as T
    }

    const res = await fetch(url, {
      ...init,
      signal: ctrl.signal,
      headers: {
        ...(init?.headers || {}),
        'X-Tenant': tenant,
        'Content-Type': init?.body ? 'application/json' : (init?.headers as any)?.['Content-Type'] || 'application/json',
      },
    })
    if (!res.ok) {
      const text = await res.text().catch(() => '')
      throw new Error(`HTTP ${res.status} ${res.statusText} for ${url} :: ${text}`)
    }
    // 204 no content?
    if (res.status === 204) return {} as T
    return (await res.json()) as T
  } finally {
    clearTimeout(timer)
  }
}

export function setTenant(next: string) {
  localStorage.setItem('tenant', next)
  // No auto-reload here; component decides
}
