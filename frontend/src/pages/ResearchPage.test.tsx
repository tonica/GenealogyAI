import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ResearchPage } from '@/pages/ResearchPage'
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

const tasks = [
  {
    person_id: 1,
    xref: 'I1',
    objective: 'Buscar el baptisme de John Garcia',
    kind: 'birth',
    hypothesis: 'Data possible 1880-1900',
    related_person_ids: [],
    status: 'open',
    priority: 'medium',
  },
  {
    person_id: 2,
    xref: 'I2',
    objective: 'Revisar possible duplicat entre John Garcia i Joan Garcia',
    kind: 'duplicate',
    hypothesis: 'Similitud 0.80',
    related_person_ids: [3],
    status: 'open',
    priority: 'high',
  },
]

describe('ResearchPage', () => {
  beforeEach(() => {
    apiMock.researchTasks.mockReset()
  })

  it('mostra les tasques agrupades per tipus', async () => {
    apiMock.researchTasks.mockResolvedValue(tasks)
    renderWithProviders(<ResearchPage />)

    await waitFor(() => {
      expect(
        screen.getByText('Buscar el baptisme de John Garcia'),
      ).toBeInTheDocument()
    })
    expect(
      screen.getByText('Revisar possible duplicat entre John Garcia i Joan Garcia'),
    ).toBeInTheDocument()
  })

  it('filtra per prioritat', async () => {
    apiMock.researchTasks.mockResolvedValue(tasks)
    renderWithProviders(<ResearchPage />)

    await waitFor(() => {
      expect(screen.getByText('Tasques de recerca')).toBeInTheDocument()
    })

    await userEvent.selectOptions(screen.getByLabelText('Prioritat'), 'high')

    await waitFor(() => {
      expect(
        screen.getByText('Revisar possible duplicat entre John Garcia i Joan Garcia'),
      ).toBeInTheDocument()
    })
    expect(screen.queryByText('Buscar el baptisme de John Garcia')).not.toBeInTheDocument()
  })

  it('filtra per tipus', async () => {
    apiMock.researchTasks.mockResolvedValue(tasks)
    renderWithProviders(<ResearchPage />)

    await waitFor(() => {
      expect(screen.getByText('Tasques de recerca')).toBeInTheDocument()
    })

    await userEvent.selectOptions(screen.getByLabelText('Tipus'), 'birth')

    await waitFor(() => {
      expect(screen.getByText('Buscar el baptisme de John Garcia')).toBeInTheDocument()
    })
    expect(
      screen.queryByText('Revisar possible duplicat entre John Garcia i Joan Garcia'),
    ).not.toBeInTheDocument()
  })

  it('mostra un estat buit quan no hi ha tasques', async () => {
    apiMock.researchTasks.mockResolvedValue([])
    renderWithProviders(<ResearchPage />)

    await waitFor(() => {
      expect(screen.getByText('Cap tasca amb aquests filtres')).toBeInTheDocument()
    })
  })
})
