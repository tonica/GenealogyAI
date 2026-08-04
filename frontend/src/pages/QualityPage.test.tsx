import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QualityPage } from '@/pages/QualityPage'
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

const report = {
  total: 3,
  errors: [
    {
      category: 'dates',
      severity: 'error',
      message: 'Data de defunció anterior al naixement',
      ref: 'I1',
      metadata: {},
    },
  ],
  warnings: [
    {
      category: 'completeness',
      severity: 'warning',
      message: 'persona sense naixement',
      ref: 'I2',
      metadata: {},
    },
  ],
  infos: [
    {
      category: 'place',
      severity: 'info',
      message: 'Topònim inconsistent',
      ref: 'I3',
      metadata: {},
    },
  ],
}

const statistics = {
  persons: 3,
  families: 1,
  sources: 0,
  media: 0,
  events: 3,
  males: 2,
  females: 1,
  average_age: null,
  max_age: null,
  events_by_type: {},
  sex_by: { M: 2, F: 1 },
  surname_frequency: {},
  persons_without_name: 1,
  persons_without_data: 0,
  birth_year_range: [null, null],
  births_by_year: {},
  deaths_by_year: {},
  top_places: [],
  top_surnames: [],
  largest_branches: [],
}

const duplicates = [
  {
    person_a: { id: 1, xref: 'I1', name: 'John Garcia' },
    person_b: { id: 2, xref: 'I2', name: 'Joan Garcia' },
    score: 0.8,
    confidence: 0.8,
    rules_used: ['name'],
    reasons: ['name-match'],
  },
]

describe('QualityPage', () => {
  beforeEach(() => {
    apiMock.qualityReport.mockReset()
    apiMock.duplicates.mockReset()
    apiMock.statistics.mockReset()
  })

  it('mostra els errors', async () => {
    apiMock.qualityReport.mockResolvedValue(report)
    apiMock.duplicates.mockResolvedValue([])
    apiMock.statistics.mockResolvedValue(statistics)
    renderWithProviders(<QualityPage />)

    await waitFor(() => {
      expect(
        screen.getByText('Data de defunció anterior al naixement'),
      ).toBeInTheDocument()
    })
  })

  it('mostra les persones incompletes', async () => {
    apiMock.qualityReport.mockResolvedValue(report)
    apiMock.duplicates.mockResolvedValue([])
    apiMock.statistics.mockResolvedValue(statistics)
    renderWithProviders(<QualityPage />)

    await waitFor(() => {
      expect(screen.getByText('Qualitat de les dades')).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole('button', { name: /Persones incompletes/ }))
    await waitFor(() => {
      expect(screen.getByText('persona sense naixement')).toBeInTheDocument()
    })
  })

  it('mostra els topònims', async () => {
    apiMock.qualityReport.mockResolvedValue(report)
    apiMock.duplicates.mockResolvedValue([])
    apiMock.statistics.mockResolvedValue(statistics)
    renderWithProviders(<QualityPage />)

    await waitFor(() => {
      expect(screen.getByText('Qualitat de les dades')).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole('button', { name: /Topònims/ }))
    await waitFor(() => {
      expect(screen.getByText('Topònim inconsistent')).toBeInTheDocument()
    })
  })

  it('mostra els duplicats', async () => {
    apiMock.qualityReport.mockResolvedValue(report)
    apiMock.duplicates.mockResolvedValue(duplicates)
    apiMock.statistics.mockResolvedValue(statistics)
    renderWithProviders(<QualityPage />)

    await waitFor(() => {
      expect(screen.getByText('Qualitat de les dades')).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole('button', { name: /Duplicats/ }))
    await waitFor(() => {
      expect(screen.getByText(/John Garcia/)).toBeInTheDocument()
      expect(screen.getByText(/Joan Garcia/)).toBeInTheDocument()
    })
  })
})
