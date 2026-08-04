import { describe, it, expect, vi } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import { DashboardPage } from '@/pages/DashboardPage'
import { renderWithProviders } from '@/test/utils'
import { apiMock } from '@/test/api-mock'

vi.mock('@/api/client', async () => {
  const { apiMock } = await import('@/test/api-mock')
  return {
    api: apiMock,
    ApiError: class extends Error {
      status: number
      constructor(status: number, message: string) {
        super(message)
        this.status = status
      }
    },
  }
})

const dashboard = {
  persons: 10,
  families: 4,
  events: 12,
  places: 3,
  sources: 2,
  media: 0,
  males: 6,
  females: 4,
  average_age: 71.5,
  average_quality: 0.65,
  duplicates: 2,
  pending_tasks: 7,
  last_import: '2026-07-01T10:00:00',
}

describe('DashboardPage', () => {
  it('mostra les mètriques principals', async () => {
    apiMock.dashboard.mockResolvedValue(dashboard)
    renderWithProviders(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText('Persones')).toBeInTheDocument()
    })

    expect(screen.getByText('10')).toBeInTheDocument()
    expect(screen.getByText('4')).toBeInTheDocument()
    expect(screen.getByText('12')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
  })

  it('mostra la qualitat mitjana', async () => {
    apiMock.dashboard.mockResolvedValue(dashboard)
    renderWithProviders(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText('65%')).toBeInTheDocument()
    })
  })

  it('mostra les tasques pendents', async () => {
    apiMock.dashboard.mockResolvedValue(dashboard)
    renderWithProviders(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText('7')).toBeInTheDocument()
    })
  })

  it("gestiona l'estat de càrrega", () => {
    apiMock.dashboard.mockReturnValue(new Promise(() => {}))
    renderWithProviders(<DashboardPage />)
    expect(screen.getByRole('status')).toBeInTheDocument()
  })

  it('mostra un estat buit si hi ha error', async () => {
    apiMock.dashboard.mockRejectedValue(new Error('boom'))
    renderWithProviders(<DashboardPage />)
    await waitFor(() => {
      expect(
        screen.getByText("No s'ha pogut carregar el resum"),
      ).toBeInTheDocument()
    })
  })
})
