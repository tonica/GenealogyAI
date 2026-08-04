import { Link, useParams } from 'react-router-dom'
import { useFamily } from '@/hooks/queries'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Loading } from '@/components/ui/Loading'
import { EmptyState } from '@/components/ui/EmptyState'
import { Breadcrumbs } from '@/components/layout/Breadcrumbs'
import { formatEventType, formatLifespan } from '@/utils/format'
import type { PersonSummary } from '@/types/dto'

function PersonLink({ person, label }: { person: PersonSummary | null; label: string }) {
  if (!person) {
    return (
      <div className="flex items-center justify-center rounded-lg border border-dashed border-slate-300 p-4 text-sm text-slate-400 dark:border-slate-600">
        {label}
      </div>
    )
  }
  return (
    <Link
      to={`/persons/${person.id}`}
      className="group flex flex-col items-center gap-1 rounded-lg border border-slate-200 p-4 text-center transition-colors hover:border-brand-400 hover:bg-brand-50 dark:border-slate-700 dark:hover:bg-slate-800"
    >
      <span className="text-sm font-semibold text-slate-900 group-hover:text-brand-700 dark:text-slate-100">
        {person.display_name}
      </span>
      <span className="text-xs text-slate-500 dark:text-slate-400">
        {formatLifespan(person.birth_year, person.death_year)}
      </span>
    </Link>
  )
}

export function FamilyPage() {
  const { familyId } = useParams<{ familyId: string }>()
  const id = Number(familyId)
  const { data, isLoading, isError } = useFamily(id)

  if (isLoading) return <Loading full label="Carregant la família…" />

  if (isError || !data) {
    return (
      <>
        <Breadcrumbs items={[{ label: 'Inici', to: '/' }, { label: 'Família' }]} />
        <Card>
          <EmptyState
            title="Família no trobada"
            description="La família no existeix o el backend no està disponible."
          />
        </Card>
      </>
    )
  }

  return (
    <div className="space-y-6">
      <Breadcrumbs
        items={[{ label: 'Inici', to: '/' }, { label: `Família ${data.id}` }]}
      />

      <div className="flex flex-wrap items-center gap-3">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
          Família {data.id}
        </h2>
        {data.marriage_date && (
          <Badge tone="neutral">Casats el {data.marriage_date}</Badge>
        )}
        {data.marriage_place && (
          <Badge tone="neutral">Lloc: {data.marriage_place}</Badge>
        )}
      </div>

      <div className="grid gap-3 md:grid-cols-[1fr_auto_1fr]">
        <PersonLink person={data.father} label="Pare desconegut" />
        <div className="flex items-center justify-center text-slate-400">⚭</div>
        <PersonLink person={data.mother} label="Mare desconeguda" />
      </div>

      <Card title="Fills" subtitle={`${data.children.length} fills`}>
        {data.children.length === 0 ? (
          <EmptyState title="Cap fill registrat" />
        ) : (
          <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {data.children.map((child) => (
              <li key={child.id}>
                <Link
                  to={`/persons/${child.id}`}
                  className="flex flex-col rounded-lg border border-slate-200 p-3 transition-colors hover:border-brand-400 hover:bg-brand-50 dark:border-slate-700 dark:hover:bg-slate-800"
                >
                  <span className="text-sm font-medium text-slate-900 dark:text-slate-100">
                    {child.display_name}
                  </span>
                  <span className="text-xs text-slate-500 dark:text-slate-400">
                    {formatLifespan(child.birth_year, child.death_year)}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </Card>

      {data.events.length > 0 && (
        <Card title="Esdeveniments de la família">
          <ul className="space-y-2 text-sm">
            {data.events.map((event) => (
              <li key={event.id} className="flex items-center gap-3">
                <Badge tone="info">{formatEventType(event.event_type)}</Badge>
                <span className="text-slate-700 dark:text-slate-300">
                  {event.date_text || '—'}
                  {event.place ? ` · ${event.place}` : ''}
                </span>
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  )
}
