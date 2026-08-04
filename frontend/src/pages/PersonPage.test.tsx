import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import { PersonPage } from '@/pages/PersonPage'
import { renderPageWithRoutes } from '@/test/utils'
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

const person = {
  id: 1,
  xref: '@I1@',
  given_name: 'John',
  surname: 'Garcia',
  prefix: null,
  suffix: null,
  sex: 'M',
  display_name: 'John Garcia',
  birth_date: '10 FEB 1890',
  death_date: '3 MAR 1970',
  birth_year: 1890,
  death_year: 1970,
  birth_place: 'Barcelona',
  death_place: 'Madrid',
  quality: 0.8,
  notes: 'Notes de prova',
  birth: {
    id: 11,
    event_type: 'birth',
    date_text: '10 FEB 1890',
    date_iso: '1890-02-10',
    date_year: 1890,
    place: 'Barcelona',
    place_id: 1,
    description: null,
    sort_year: 1890,
  },
  death: null,
  parents: [
    {
      id: 2,
      xref: '@I2@',
      given_name: 'Pep',
      surname: 'Garcia',
      prefix: null,
      suffix: null,
      sex: 'M',
      display_name: 'Pep Garcia',
      birth_date: null,
      death_date: null,
      birth_year: null,
      death_year: null,
      birth_place: null,
      death_place: null,
      quality: 0.5,
    },
  ],
  spouses: [],
  children: [
    {
      id: 3,
      xref: '@I3@',
      given_name: 'Anna',
      surname: 'Garcia',
      prefix: null,
      suffix: null,
      sex: 'F',
      display_name: 'Anna Garcia',
      birth_date: '1920-01-01',
      death_date: null,
      birth_year: 1920,
      death_year: null,
      birth_place: null,
      death_place: null,
      quality: 0.6,
    },
  ],
  events: [],
  timeline: [
    {
      id: 11,
      event_type: 'birth',
      date_text: '10 FEB 1890',
      date_iso: '1890-02-10',
      date_year: 1890,
      place: 'Barcelona',
      place_id: 1,
      description: null,
      sort_year: 1890,
    },
  ],
  quality_detail: {
    person_id: 1,
    xref: '@I1@',
    score: 0.8,
    missing: [],
    issues: [],
    factors: [],
  },
  duplicates: [],
  tasks: [],
}

describe('PersonPage', () => {
  beforeEach(() => {
    apiMock.person.mockReset()
  })

  it('mostra el nom i les dades vitals', async () => {
    apiMock.person.mockResolvedValue(person)
    renderPageWithRoutes(<PersonPage />, '/persons/:personId', '/persons/1')

    await waitFor(() => {
      expect(screen.getAllByText('John Garcia').length).toBeGreaterThan(0)
    })
    expect(screen.getAllByText(/10 FEB 1890 · Barcelona/).length).toBeGreaterThan(0)
  })

  it('mostra els pares', async () => {
    apiMock.person.mockResolvedValue(person)
    renderPageWithRoutes(<PersonPage />, '/persons/:personId', '/persons/1')

    await waitFor(() => {
      expect(screen.getByText('Pep Garcia')).toBeInTheDocument()
    })
  })

  it('mostra els fills', async () => {
    apiMock.person.mockResolvedValue(person)
    renderPageWithRoutes(<PersonPage />, '/persons/:personId', '/persons/1')

    await waitFor(() => {
      expect(screen.getByText('Anna Garcia')).toBeInTheDocument()
    })
  })

  it('mostra la línia del temps', async () => {
    apiMock.person.mockResolvedValue(person)
    renderPageWithRoutes(<PersonPage />, '/persons/:personId', '/persons/1')

    await waitFor(() => {
      expect(screen.getAllByText('Línia del temps').length).toBeGreaterThan(0)
    })
    expect(screen.getAllByText('Naixement').length).toBeGreaterThan(0)
  })

  it('mostra l\'estat de càrrega', () => {
    apiMock.person.mockReturnValue(new Promise(() => {}))
    renderPageWithRoutes(<PersonPage />, '/persons/:personId', '/persons/1')
    expect(screen.getByRole('status')).toBeInTheDocument()
  })

  it('mostra persona no trobada', async () => {
    apiMock.person.mockRejectedValue(new Error('no'))
    renderPageWithRoutes(<PersonPage />, '/persons/:personId', '/persons/999')
    await waitFor(() => {
      expect(screen.getByText('Persona no trobada')).toBeInTheDocument()
    })
  })
})
