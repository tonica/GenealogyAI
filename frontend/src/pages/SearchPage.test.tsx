import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { SearchPage } from '@/pages/SearchPage'
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

const persons = [
  {
    id: 1,
    xref: '@I1@',
    given_name: 'John',
    surname: 'Garcia',
    prefix: null,
    suffix: null,
    sex: 'M',
    display_name: 'John Garcia',
    birth_date: '10 FEB 1890',
    death_date: null,
    birth_year: 1890,
    death_year: null,
    birth_place: 'Barcelona',
    death_place: null,
    quality: 0.7,
  },
]

describe('SearchPage', () => {
  beforeEach(() => {
    apiMock.searchPersons.mockReset()
  })

  it('mostra els resultats de la cerca', async () => {
    apiMock.searchPersons.mockResolvedValue(persons)
    renderWithProviders(<SearchPage />)

    await waitFor(() => {
      expect(screen.getByText('John Garcia')).toBeInTheDocument()
    })
    expect(screen.getByText(/· Barcelona/)).toBeInTheDocument()
  })

  it('mostra un estat buit quan no hi ha resultats', async () => {
    apiMock.searchPersons.mockResolvedValue([])
    renderWithProviders(<SearchPage />)

    await waitFor(() => {
      expect(screen.getByText('Cap resultat')).toBeInTheDocument()
    })
  })

  it('torna a cercar en netejar els filtres', async () => {
    apiMock.searchPersons.mockResolvedValue(persons)
    renderWithProviders(<SearchPage />)

    await waitFor(() => {
      expect(screen.getByText('John Garcia')).toBeInTheDocument()
    })

    const callsBeforeTyping = apiMock.searchPersons.mock.calls.length

    const input = screen.getByPlaceholderText('Per exemple: Maria')
    await userEvent.type(input, 'Maria')
    await waitFor(() => {
      expect(apiMock.searchPersons.mock.calls.length).toBeGreaterThan(
        callsBeforeTyping,
      )
    })

    const button = screen.getByRole('button', { name: 'Neteja' })
    await userEvent.click(button)
    await waitFor(() => {
      expect(apiMock.searchPersons.mock.calls.length).toBeGreaterThan(
        callsBeforeTyping + 1,
      )
    })
  })

  it("gestiona l'error de connexió", async () => {
    apiMock.searchPersons.mockRejectedValue(new Error('offline'))
    renderWithProviders(<SearchPage />)

    await waitFor(() => {
      expect(screen.getByText('Error en la cerca')).toBeInTheDocument()
    })
  })
})
