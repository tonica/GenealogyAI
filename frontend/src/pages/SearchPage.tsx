import { useMemo } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { usePersons } from '@/hooks/queries'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Table } from '@/components/ui/Table'
import { Loading } from '@/components/ui/Loading'
import { EmptyState } from '@/components/ui/EmptyState'
import {
  formatLifespan,
  formatPercent,
  formatSex,
  qualityLabel,
} from '@/utils/format'
import type { PersonSummary } from '@/types/dto'

const searchSchema = z.object({
  q: z.string().optional(),
  surname: z.string().optional(),
  given_name: z.string().optional(),
  sex: z.enum(['', 'M', 'F', 'U']).optional(),
  place: z.string().optional(),
  birth_year: z
    .string()
    .optional()
    .refine((v) => v === undefined || v === '' || /^\d{4}$/.test(v), {
      message: 'Any de 4 xifres',
    }),
})

type SearchForm = z.infer<typeof searchSchema>

const DEFAULT_VALUES: SearchForm = {
  q: '',
  surname: '',
  given_name: '',
  sex: '',
  place: '',
  birth_year: '',
}

export function SearchPage() {
  const { register, handleSubmit, reset, watch } = useForm<SearchForm>({
    resolver: zodResolver(searchSchema),
    defaultValues: DEFAULT_VALUES,
  })

  const watched = watch()
  const query = useMemo(
    () => ({
      q: watched.q || undefined,
      surname: watched.surname || undefined,
      given_name: watched.given_name || undefined,
      sex: (watched.sex || undefined) as 'M' | 'F' | 'U' | undefined,
      place: watched.place || undefined,
      birth_year: watched.birth_year ? Number(watched.birth_year) : undefined,
      limit: 50,
    }),
    [watched],
  )
  const { data, isLoading, isError } = usePersons(query)

  const handleReset = () => {
    reset(DEFAULT_VALUES)
  }

  const columns = [
    { key: 'name', header: 'Persona' },
    { key: 'sex', header: 'Sexe' },
    { key: 'lifespan', header: 'Naix. – Def. (lloc)' },
    { key: 'quality', header: 'Qualitat' },
  ]

  const rows = (data ?? []).map((p: PersonSummary) => [
    <span key="name" className="font-medium text-slate-900 dark:text-slate-100">
      {p.display_name}
    </span>,
    <Badge key="sex" tone={p.sex === 'F' ? 'info' : p.sex === 'M' ? 'default' : 'neutral'}>
      {formatSex(p.sex)}
    </Badge>,
    <span key="life">
      {formatLifespan(p.birth_year, p.death_year)}
      {p.birth_place ? ` · ${p.birth_place}` : ''}
    </span>,
    <span key="quality">
      {p.quality !== null ? (
        <>
          {formatPercent(p.quality)}{' '}
          <span className="text-xs text-slate-400">({qualityLabel(p.quality)})</span>
        </>
      ) : (
        '—'
      )}
    </span>,
  ])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">Cerca</h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Filtra per nom, cognom, sexe, lloc o any de naixement.
        </p>
      </div>

      <Card title="Filtres de cerca">
        <form onSubmit={handleSubmit(() => {})} className="grid gap-3 lg:grid-cols-3">
          <label className="block text-sm">
            <span className="mb-1 block font-medium text-slate-700 dark:text-slate-300">
              Nom o text lliure
            </span>
            <input
              {...register('q')}
              placeholder="Per exemple: Maria"
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
            />
          </label>
          <label className="block text-sm">
            <span className="mb-1 block font-medium text-slate-700 dark:text-slate-300">
              Cognom
            </span>
            <input
              {...register('surname')}
              placeholder="Per exemple: Garcia"
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
            />
          </label>
          <label className="block text-sm">
            <span className="mb-1 block font-medium text-slate-700 dark:text-slate-300">
              Lloc
            </span>
            <input
              {...register('place')}
              placeholder="Per exemple: Barcelona"
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
            />
          </label>
          <label className="block text-sm">
            <span className="mb-1 block font-medium text-slate-700 dark:text-slate-300">
              Sexe
            </span>
            <select
              {...register('sex')}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
            >
              <option value="">Tots</option>
              <option value="M">Home</option>
              <option value="F">Dona</option>
              <option value="U">Desconegut</option>
            </select>
          </label>
          <label className="block text-sm">
            <span className="mb-1 block font-medium text-slate-700 dark:text-slate-300">
              Any de naixement
            </span>
            <input
              {...register('birth_year')}
              placeholder="Ex: 1890"
              inputMode="numeric"
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
            />
          </label>
          <div className="flex items-end gap-2">
            <Button variant="secondary" onClick={handleReset} className="w-full lg:w-auto">
              Neteja
            </Button>
          </div>
        </form>
      </Card>

      {isLoading && <Loading full label="Buscant…" />}

      {isError && (
        <Card>
          <EmptyState
            title="Error en la cerca"
            description="No s'ha pogut consultar el backend. Revisa la connexió."
          />
        </Card>
      )}

      {!isLoading && !isError && (
        <Card title="Resultats" subtitle={`${data?.length ?? 0} persones`}>
          {data && data.length > 0 ? (
            <Table
              columns={columns}
              rows={rows}
              onRowClick={(index) => {
                const p = data[index]
                if (p) window.location.href = `/persons/${p.id}`
              }}
            />
          ) : (
            <EmptyState
              title="Cap resultat"
              description="Prova d'ampliar els filtres o de netejar la cerca."
            />
          )}
        </Card>
      )}

      <div className="mt-4">
        <Link
          to="/families"
          className="text-sm font-medium text-brand-600 hover:text-brand-700 dark:text-brand-400"
        >
          Explorar famílies →
        </Link>
      </div>
    </div>
  )
}