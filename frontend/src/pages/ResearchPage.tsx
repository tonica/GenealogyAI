import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useResearchTasks } from '@/hooks/queries'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Loading } from '@/components/ui/Loading'
import { EmptyState } from '@/components/ui/EmptyState'
import { Breadcrumbs } from '@/components/layout/Breadcrumbs'
import type { ResearchTask } from '@/types/dto'

const KIND_TONES: Record<string, 'info' | 'warning' | 'default' | 'neutral' | 'success' | 'danger'> = {
  birth: 'success',
  death: 'warning',
  marriage: 'info',
  parents: 'default',
  duplicate: 'danger',
}

const PRIORITY_TONES: Record<string, 'info' | 'warning' | 'default' | 'neutral' | 'success' | 'danger'> = {
  high: 'danger',
  medium: 'warning',
  low: 'info',
}

const STATUS_TONES: Record<string, 'info' | 'warning' | 'default' | 'neutral' | 'success' | 'danger'> = {
  open: 'info',
  in_progress: 'warning',
  done: 'success',
}

type StatusFilter = 'all' | 'open' | 'in_progress' | 'done'
type PriorityFilter = 'all' | 'high' | 'medium' | 'low'
type KindFilter = 'all' | string

export function ResearchPage() {
  const { data, isLoading, isError } = useResearchTasks()
  const [status, setStatus] = useState<StatusFilter>('all')
  const [priority, setPriority] = useState<PriorityFilter>('all')
  const [kind, setKind] = useState<KindFilter>('all')
  const [personQuery, setPersonQuery] = useState('')

  const kinds = useMemo(() => {
    const set = new Set((data ?? []).map((t) => t.kind))
    return Array.from(set).sort()
  }, [data])

  const filtered = useMemo(() => {
    const q = personQuery.trim().toLowerCase()
    return (data ?? []).filter((task) => {
      if (status !== 'all' && task.status !== status) return false
      if (priority !== 'all' && task.priority !== priority) return false
      if (kind !== 'all' && task.kind !== kind) return false
      if (q && !`${task.objective} ${task.xref ?? ''}`.toLowerCase().includes(q)) return false
      return true
    })
  }, [data, status, priority, kind, personQuery])

  if (isLoading) return <Loading full label="Generant tasques de recerca…" />

  if (isError || !data) {
    return (
      <>
        <Breadcrumbs items={[{ label: 'Inici', to: '/' }, { label: 'Recerca' }]} />
        <Card>
          <EmptyState
            title="No s'han pogut generar les tasques"
            description="Revisa que el backend estigui disponible."
          />
        </Card>
      </>
    )
  }

  const byKind = filtered.reduce<Record<string, ResearchTask[]>>((acc, task) => {
    const tasks = acc[task.kind] ?? []
    acc[task.kind] = [...tasks, task]
    return acc
  }, {})

  const selectClass =
    'rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100'

  return (
    <div className="space-y-6">
      <Breadcrumbs items={[{ label: 'Inici', to: '/' }, { label: 'Recerca' }]} />
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">
          Tasques de recerca
        </h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          {filtered.length} de {data.length} suggeriments generats a partir de les
          mancances de dades.
        </p>
      </div>

      <Card title="Filtres">
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          <label className="block text-sm">
            <span className="mb-1 block font-medium text-slate-700 dark:text-slate-300">Estat</span>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value as StatusFilter)}
              className={selectClass}
            >
              <option value="all">Tots</option>
              <option value="open">Oberta</option>
              <option value="in_progress">En curs</option>
              <option value="done">Feta</option>
            </select>
          </label>

          <label className="block text-sm">
            <span className="mb-1 block font-medium text-slate-700 dark:text-slate-300">Prioritat</span>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as PriorityFilter)}
              className={selectClass}
            >
              <option value="all">Totes</option>
              <option value="high">Alta</option>
              <option value="medium">Mitjana</option>
              <option value="low">Baixa</option>
            </select>
          </label>

          <label className="block text-sm">
            <span className="mb-1 block font-medium text-slate-700 dark:text-slate-300">Tipus</span>
            <select
              value={kind}
              onChange={(e) => setKind(e.target.value as KindFilter)}
              className={selectClass}
            >
              <option value="all">Tots</option>
              {kinds.map((k) => (
                <option key={k} value={k}>{k}</option>
              ))}
            </select>
          </label>

          <label className="block text-sm">
            <span className="mb-1 block font-medium text-slate-700 dark:text-slate-300">Persona</span>
            <input
              value={personQuery}
              onChange={(e) => setPersonQuery(e.target.value)}
              placeholder="Filtra per persona…"
              className={selectClass}
            />
          </label>
        </div>
        <div className="mt-3">
          <Button variant="secondary" size="sm" onClick={() => {
            setStatus('all')
            setPriority('all')
            setKind('all')
            setPersonQuery('')
          }}>
            Neteja filtres
          </Button>
        </div>
      </Card>

      {filtered.length === 0 ? (
        <Card>
          <EmptyState
            title="Cap tasca amb aquests filtres"
            description="Prova de relaxar els filtres."
          />
        </Card>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {Object.entries(byKind).map(([k, tasks]) => (
            <Card
              key={k}
              title={k}
              subtitle={`${tasks.length} tasques`}
            >
              <ul className="space-y-3">
                {tasks.slice(0, 12).map((task, index) => (
                  <li
                    key={index}
                    className="rounded-lg border border-slate-100 p-3 dark:border-slate-700"
                  >
                    <p className="text-sm font-medium text-slate-800 dark:text-slate-200">
                      {task.objective}
                    </p>
                    <div className="mt-1 flex flex-wrap items-center gap-2 text-xs">
                      <Badge tone={KIND_TONES[task.kind] ?? 'neutral'}>
                        {task.kind}
                      </Badge>
                      <Badge tone={PRIORITY_TONES[task.priority] ?? 'neutral'}>
                        {task.priority}
                      </Badge>
                      <Badge tone={STATUS_TONES[task.status] ?? 'neutral'}>
                        {task.status}
                      </Badge>
                      {task.hypothesis && (
                        <span className="text-slate-500 dark:text-slate-400">
                          {task.hypothesis}
                        </span>
                      )}
                      {task.person_id !== null && task.person_id !== undefined && (
                        <Link
                          to={`/persons/${task.person_id}`}
                          className="text-brand-600 hover:underline dark:text-brand-400"
                        >
                          Veure persona →
                        </Link>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
