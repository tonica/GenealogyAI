// Client API centralitzat: totes les crides al backend passen per aquí.
// Base URL = /api/v1 (dev proxied pel Vite; prod servit pel Docker).

import type {
  Dashboard,
  DuplicateCandidate,
  Family,
  PersonDetails,
  PersonQuality,
  PersonSearchParams,
  PersonSummary,
  QualityReport,
  ResearchTask,
  Statistics,
} from '@/types/dto'

const BASE_URL = '/api/v1'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
    this.name = 'ApiError'
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      headers: { Accept: 'application/json' },
      ...init,
    })
  } catch (err) {
    throw new ApiError(0, `No es pot connectar amb el servidor: ${String(err)}`)
  }
  if (!res.ok) {
    let detail = `Error HTTP ${res.status}`
    try {
      const body = await res.json()
      if (body?.detail) detail = String(body.detail)
    } catch {
      /* cos no JSON */
    }
    throw new ApiError(res.status, detail)
  }
  return res.json() as Promise<T>
}

function buildQuery(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, String(value))
    }
  }
  const qs = search.toString()
  return qs ? `?${qs}` : ''
}

export const api = {
  // --- Dashboard ---
  dashboard: () => request<Dashboard>('/dashboard'),

  // --- Persones ---
  searchPersons: (params: PersonSearchParams = {}) =>
    request<PersonSummary[]>(`/persons${buildQuery(params as never)}`),
  person: (id: number) => request<PersonDetails>(`/persons/${id}`),
  personQuality: (id: number) => request<PersonQuality>(`/quality/persons/${id}`),

  // --- Famílies ---
  families: (limit = 50, offset = 0) =>
    request<Family[]>(`/families?limit=${limit}&offset=${offset}`),
  family: (id: number) => request<Family>(`/families/${id}`),

  // --- Intel·ligència ---
  statistics: () => request<Statistics>('/statistics'),
  qualityReport: () => request<QualityReport>('/quality/report'),
  duplicates: (limit = 50) => request<DuplicateCandidate[]>(`/duplicates?limit=${limit}`),
  researchTasks: (limit = 200) =>
    request<ResearchTask[]>(`/research/tasks?limit=${limit}`),
}

export default api
