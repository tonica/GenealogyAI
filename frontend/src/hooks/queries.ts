import { useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/api/client'

export const queryKeys = {
  dashboard: ['dashboard'] as const,
  persons: (params: unknown) => ['persons', params] as const,
  person: (id: number) => ['person', id] as const,
  families: (limit: number, offset: number) =>
    ['families', limit, offset] as const,
  family: (id: number) => ['family', id] as const,
  statistics: ['statistics'] as const,
  qualityReport: ['quality-report'] as const,
  duplicates: ['duplicates'] as const,
  researchTasks: ['research-tasks'] as const,
}

export function useDashboard() {
  return useQuery({
    queryKey: queryKeys.dashboard,
    queryFn: api.dashboard,
  })
}

export function usePersons(params: {
  q?: string
  surname?: string
  given_name?: string
  sex?: 'M' | 'F' | 'U'
  place?: string
  birth_year?: number
  limit?: number
  offset?: number
}) {
  return useQuery({
    queryKey: queryKeys.persons(params),
    queryFn: () => api.searchPersons(params),
    placeholderData: (prev) => prev,
  })
}

export function usePerson(id: number) {
  return useQuery({
    queryKey: queryKeys.person(id),
    queryFn: () => api.person(id),
    enabled: Number.isFinite(id),
  })
}

export function useFamilies(limit = 50, offset = 0) {
  return useQuery({
    queryKey: queryKeys.families(limit, offset),
    queryFn: () => api.families(limit, offset),
  })
}

export function useFamily(id: number) {
  return useQuery({
    queryKey: queryKeys.family(id),
    queryFn: () => api.family(id),
    enabled: Number.isFinite(id),
  })
}

export function useStatistics() {
  return useQuery({ queryKey: queryKeys.statistics, queryFn: api.statistics })
}

export function useQualityReport() {
  return useQuery({
    queryKey: queryKeys.qualityReport,
    queryFn: api.qualityReport,
  })
}

export function useDuplicates() {
  return useQuery({
    queryKey: queryKeys.duplicates,
    queryFn: () => api.duplicates(),
  })
}

export function useResearchTasks() {
  return useQuery({
    queryKey: queryKeys.researchTasks,
    queryFn: () => api.researchTasks(),
  })
}

export function useInvalidateDashboard() {
  const queryClient = useQueryClient()
  return () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.dashboard })
  }
}
