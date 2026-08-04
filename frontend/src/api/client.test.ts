import { describe, it, expect, vi, afterEach } from 'vitest'
import { api, ApiError } from '@/api/client'

describe('api client', () => {
  const fetchMock = vi.fn()
  vi.stubGlobal('fetch', fetchMock)

  afterEach(() => {
    fetchMock.mockReset()
  })

  it('construyeix les URLs sota /api/v1', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({ persons: 1 }),
    })
    await api.dashboard()
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/dashboard',
      expect.objectContaining({ headers: { Accept: 'application/json' } }),
    )
  })

  it('serialitza els paràmetres de cerca', async () => {
    fetchMock.mockResolvedValue({ ok: true, json: async () => [] })
    await api.searchPersons({ q: 'Maria', birth_year: 1890 })
    const url = fetchMock.mock.calls[0][0]
    expect(url).toContain('/api/v1/persons?')
    expect(url).toContain('q=Maria')
    expect(url).toContain('birth_year=1890')
  })

  it('ignora els paràmetres buits', async () => {
    fetchMock.mockResolvedValue({ ok: true, json: async () => [] })
    await api.searchPersons({ q: '', sex: undefined })
    const url = fetchMock.mock.calls[0][0]
    expect(url).not.toContain('q=')
    expect(url).not.toContain('sex=')
  })

  it('llença ApiError amb el missatge del backend', async () => {
    fetchMock.mockResolvedValue({
      ok: false,
      status: 404,
      json: async () => ({ detail: 'Persona no trobada' }),
    })
    await expect(api.person(123)).rejects.toMatchObject({
      status: 404,
      message: 'Persona no trobada',
    })
  })

  it('es capaç de connectar amb el servidor', async () => {
    const originalFetch = globalThis.fetch
    globalThis.fetch = vi.fn(() => Promise.reject(new Error('network down')))
    try {
      await expect(api.dashboard()).rejects.toBeInstanceOf(ApiError)
    } finally {
      globalThis.fetch = originalFetch
    }
  })
})
