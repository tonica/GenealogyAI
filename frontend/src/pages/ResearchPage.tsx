import { Link } from 'react-router-dom'
import { useResearchTasks } from '@/hooks/queries'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
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

export function ResearchPage() {
  const { data, isLoading, isError } = useResearchTasks()

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

  const byKind = data.reduce<Record<string, ResearchTask[]>>((acc, task) => {
    const tasks = acc[task.kind] ?? []
    acc[task.kind] = [...tasks, task]
    return acc
  }, {})

  return (
    <div className="space-y-6">
      <Breadcrumbs items={[{ label: 'Inici', to: '/' }, { label: 'Recerca' }]} />
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">
          Tasques de recerca
        </h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          {data.length} suggeriments generats a partir de les mancances de dades.
        </p>
      </div>

      {data.length === 0 ? (
        <Card>
          <EmptyState
            title="Cap tasca suggerida"
            description="El conjunt de dades està complet o encara no hi ha prou informació."
          />
        </Card>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {Object.entries(byKind).map(([kind, tasks]) => (
            <Card
              key={kind}
              title={kind}
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
