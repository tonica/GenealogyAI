import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useQualityReport, useDuplicates, useStatistics } from '@/hooks/queries'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Table } from '@/components/ui/Table'
import { Loading } from '@/components/ui/Loading'
import { EmptyState } from '@/components/ui/EmptyState'
import { Button } from '@/components/ui/Button'
import { formatPercent } from '@/utils/format'
import type { QualityFinding } from '@/types/dto'

type Tab = 'errors' | 'warnings' | 'infos' | 'incomplete' | 'places' | 'duplicates'

export function QualityPage() {
  const { data: report, isLoading, isError } = useQualityReport()
  const { data: duplicates } = useDuplicates()
  const { data: statistics } = useStatistics()
  const [tab, setTab] = useState<Tab>('errors')

  const incomplete = useMemo(
    () =>
      (report ? [...report.warnings, ...report.infos] : []).filter(
        (f) => f.category === 'completeness',
      ),
    [report],
  )

  const places = useMemo(
    () =>
      (report ? [...report.warnings, ...report.infos] : []).filter(
        (f) => f.category === 'place' || f.category === 'toponym',
      ),
    [report],
  )

  if (isLoading) return <Loading full label="Generant l'informe de qualitat…" />

  if (isError || !report) {
    return (
      <Card>
        <EmptyState
          title="No s'ha pogut generar l'informe"
          description="Revisa que el backend estigui disponible."
        />
      </Card>
    )
  }

  const counts: Record<Tab, number> = {
    errors: report.errors.length,
    warnings: report.warnings.length,
    infos: report.infos.length,
    incomplete: incomplete.length,
    places: places.length,
    duplicates: duplicates?.length ?? 0,
  }

  const tabs: Tab[] = ['errors', 'warnings', 'infos', 'incomplete', 'places', 'duplicates']

  const columns = [
    { key: 'severity', header: 'Severitat' },
    { key: 'category', header: 'Categoria' },
    { key: 'ref', header: 'Referència' },
    { key: 'message', header: 'Observació' },
  ]

  const rows = (current: QualityFinding[]) =>
    current.map((f) => [
      <Badge
        key="sev"
        tone={f.severity === 'error' ? 'danger' : f.severity === 'warning' ? 'warning' : 'info'}
      >
        {f.severity}
      </Badge>,
      <span key="cat" className="capitalize">{f.category}</span>,
      <code key="ref" className="font-mono text-xs">{f.ref ?? '—'}</code>,
      <span key="msg">{f.message}</span>,
    ])

  const showTable = ['errors', 'warnings', 'infos', 'incomplete', 'places'].includes(tab)

  const current: QualityFinding[] =
    tab === 'incomplete'
      ? incomplete
      : tab === 'places'
        ? places
        : (report[tab as 'errors' | 'warnings' | 'infos'] ?? [])

  const tabLabels: Record<Tab, string> = {
    errors: 'Errors',
    warnings: 'Inconsistències',
    infos: 'Informació',
    incomplete: 'Persones incompletes',
    places: 'Topònims',
    duplicates: 'Duplicats',
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">
          Qualitat de les dades
        </h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          {report.total} observacions detectades al conjunt de dades.
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        {tabs.map((t) => (
          <Button
            key={t}
            variant={tab === t ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setTab(t)}
          >
            {tabLabels[t]} ({counts[t]})
          </Button>
        ))}
      </div>

      {showTable ? (
        <Card>
          {current.length === 0 ? (
            <EmptyState title="Cap observació en aquesta categoria" />
          ) : (
            <Table columns={columns} rows={rows(current)} />
          )}
        </Card>
      ) : (
        <Card title="Possibles persones duplicades" subtitle="Detectades per regles de similitud">
          {duplicates && duplicates.length > 0 ? (
            <ul className="space-y-2 text-sm">
              {duplicates.slice(0, 30).map((dup, index) => {
                const a = dup.person_a
                const b = dup.person_b
                return (
                  <li
                    key={index}
                    className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-slate-100 p-3 dark:border-slate-700"
                  >
                    <span className="text-slate-700 dark:text-slate-300">
                      {a.name}{' '}
                      {a.id !== null && (
                        <Link
                          to={`/persons/${a.id}`}
                          className="text-brand-600 hover:underline dark:text-brand-400"
                        >
                          #{a.id}
                        </Link>
                      )}{' '}
                      ↔ {b.name}{' '}
                      {b.id !== null && (
                        <Link
                          to={`/persons/${b.id}`}
                          className="text-brand-600 hover:underline dark:text-brand-400"
                        >
                          #{b.id}
                        </Link>
                      )}
                    </span>
                    <Badge tone={dup.score >= 0.7 ? 'danger' : 'warning'}>
                      {formatPercent(dup.score)}
                    </Badge>
                  </li>
                )
              })}
            </ul>
          ) : (
            <EmptyState title="Cap duplicat detectat" />
          )}
        </Card>
      )}

      {statistics && (statistics.persons_without_name > 0 || statistics.persons_without_data > 0) && (
        <Card title="Completesa del conjunt">
          <div className="flex flex-wrap gap-2">
            <Badge tone="warning">{statistics.persons_without_name} persones sense nom</Badge>
            <Badge tone="info">{statistics.persons_without_data} persones sense dades vitals</Badge>
          </div>
        </Card>
      )}
    </div>
  )
}
