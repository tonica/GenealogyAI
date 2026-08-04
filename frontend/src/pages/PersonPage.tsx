import { Link, useParams } from 'react-router-dom'
import { usePerson } from '@/hooks/queries'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Loading } from '@/components/ui/Loading'
import { EmptyState } from '@/components/ui/EmptyState'
import { Breadcrumbs } from '@/components/layout/Breadcrumbs'
import { PersonCard } from '@/features/person/PersonCard'
import { Timeline } from '@/features/person/Timeline'
import { formatPercent, formatSex, qualityLabel } from '@/utils/format'

export function PersonPage() {
  const { personId } = useParams<{ personId: string }>()
  const id = Number(personId)
  const { data, isLoading, isError } = usePerson(id)

  if (isLoading) return <Loading full label="Carregant la persona…" />

  if (isError || !data) {
    return (
      <>
        <Breadcrumbs items={[{ label: 'Inici', to: '/' }, { label: 'Persona' }]} />
        <Card>
          <EmptyState
            title="Persona no trobada"
            description="La persona no existeix o el backend no està disponible."
          />
        </Card>
      </>
    )
  }

  const quality = data.quality_detail

  return (
    <div className="space-y-6">
      <Breadcrumbs
        items={[
          { label: 'Inici', to: '/' },
          { label: 'Cerca', to: '/search' },
          { label: data.display_name },
        ]}
      />

      <div className="flex flex-wrap items-center gap-3">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
          {data.display_name}
        </h2>
        <Badge tone={data.sex === 'F' ? 'info' : data.sex === 'M' ? 'default' : 'neutral'}>
          {formatSex(data.sex)}
        </Badge>
        {quality && (
          <Badge tone={quality.score >= 0.6 ? 'success' : quality.score >= 0.4 ? 'warning' : 'danger'}>
            Qualitat {formatPercent(quality.score)} · {qualityLabel(quality.score)}
          </Badge>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-1">
          <PersonCard person={data} />

          <Card title="Dades vitals">
            <dl className="space-y-3 text-sm">
              <div>
                <dt className="text-slate-500 dark:text-slate-400">Naixement</dt>
                <dd className="font-medium text-slate-900 dark:text-slate-100">
                  {data.birth_date || '—'}
                  {data.birth_place ? ` · ${data.birth_place}` : ''}
                </dd>
              </div>
              <div>
                <dt className="text-slate-500 dark:text-slate-400">Defunció</dt>
                <dd className="font-medium text-slate-900 dark:text-slate-100">
                  {data.death_date || '—'}
                  {data.death_place ? ` · ${data.death_place}` : ''}
                </dd>
              </div>
              <div>
                <dt className="text-slate-500 dark:text-slate-400">Referència GEDCOM</dt>
                <dd className="font-mono text-slate-900 dark:text-slate-100">
                  {data.xref || '—'}
                </dd>
              </div>
            </dl>
          </Card>

          {data.notes && (
            <Card title="Notes">
              <p className="whitespace-pre-wrap text-sm text-slate-600 dark:text-slate-300">
                {data.notes}
              </p>
            </Card>
          )}

          <Card title="Fonts" subtitle={`${data.sources.length} font(s)`}>
            {data.sources.length === 0 ? (
              <EmptyState title="Cap font associada" />
            ) : (
              <ul className="space-y-3 text-sm">
                {data.sources.map((source) => (
                  <li key={source.id ?? source.xref ?? source.title}>
                    <p className="font-medium text-slate-900 dark:text-slate-100">
                      {source.title}
                    </p>
                    {(source.author || source.publication) && (
                      <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
                        {[source.author, source.publication]
                          .filter(Boolean)
                          .join(' · ')}
                      </p>
                    )}
                    {source.citation && (
                      <p className="mt-0.5 text-xs italic text-slate-400">
                        {source.citation}
                      </p>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </Card>

          {quality && (
            <Card title="Factors de qualitat" subtitle={`Puntuació ${formatPercent(quality.score)}`}>
              <ul className="space-y-2 text-sm">
                {quality.factors.map((factor) => (
                  <li
                    key={factor.name}
                    className="flex items-center justify-between gap-2"
                  >
                    <span className="capitalize text-slate-600 dark:text-slate-300">
                      {factor.name}
                    </span>
                    <Badge
                      tone={factor.contribution >= 0 ? 'success' : 'danger'}
                    >
                      {factor.contribution >= 0 ? '+' : ''}
                      {factor.contribution}
                    </Badge>
                  </li>
                ))}
              </ul>
            </Card>
          )}
        </div>

        <div className="space-y-6 lg:col-span-2">
          <div className="grid gap-6 md:grid-cols-2">
            <Card title="Pares">
              {data.parents.length === 0 ? (
                <EmptyState title="Sense pares registrats" />
              ) : (
                <ul className="space-y-2">
                  {data.parents.map((parent) => (
                    <li key={parent.id}>
                      <Link
                        to={`/persons/${parent.id}`}
                        className="text-sm font-medium text-brand-600 hover:underline dark:text-brand-400"
                      >
                        {parent.display_name}
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </Card>

            <Card title="Fills">
              {data.children.length === 0 ? (
                <EmptyState title="Sense fills registrats" />
              ) : (
                <ul className="space-y-2">
                  {data.children.map((child) => (
                    <li key={child.id}>
                      <Link
                        to={`/persons/${child.id}`}
                        className="text-sm font-medium text-brand-600 hover:underline dark:text-brand-400"
                      >
                        {child.display_name}
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </Card>
          </div>

          <Card title="Cònjuges">
            {data.spouses.length === 0 ? (
              <EmptyState title="Sense cònjuges registrats" />
            ) : (
              <ul className="space-y-3">
                {data.spouses.map((spouse) => (
                  <li key={spouse.family_id} className="flex items-center justify-between gap-2">
                    <div>
                      {spouse.spouse ? (
                        <Link
                          to={`/persons/${spouse.spouse.id}`}
                          className="text-sm font-medium text-brand-600 hover:underline dark:text-brand-400"
                        >
                          {spouse.spouse.display_name}
                        </Link>
                      ) : (
                        <span className="text-sm text-slate-400">Cònjuge desconegut</span>
                      )}
                      <div className="text-xs text-slate-500 dark:text-slate-400">
                        {spouse.marriage_date || 'Data desconeguda'}
                        {spouse.marriage_place ? ` · ${spouse.marriage_place}` : ''}
                      </div>
                    </div>
                    <Link
                      to={`/families/${spouse.family_id}`}
                      className="text-xs text-brand-600 hover:underline dark:text-brand-400"
                    >
                      Veure família →
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </Card>

          <Timeline events={data.timeline} />

          {data.duplicates.length > 0 && (
            <Card title="Possibles duplicats">
              <ul className="space-y-2 text-sm">
                {data.duplicates.map((dup, index) => {
                  const other =
                    dup.person_a.id === data.id ? dup.person_b : dup.person_a
                  return (
                    <li key={index} className="flex items-center justify-between gap-2">
                      <span>
                        Amb{' '}
                        <Link
                          to={other.id ? `/persons/${other.id}` : '#'}
                          className="font-medium text-brand-600 hover:underline dark:text-brand-400"
                        >
                          {other.name}
                        </Link>
                      </span>
                      <Badge tone={dup.score >= 0.7 ? 'danger' : 'warning'}>
                        {formatPercent(dup.score)}
                      </Badge>
                    </li>
                  )
                })}
              </ul>
            </Card>
          )}

          {data.tasks.length > 0 && (
            <Card title="Tasques de recerca">
              <ul className="space-y-2 text-sm">
                {data.tasks.map((task, index) => (
                  <li
                    key={index}
                    className="flex items-center gap-3 border-b border-slate-100 py-2 last:border-0 dark:border-slate-700"
                  >
                    <Badge tone="info">{task.kind}</Badge>
                    <span className="text-slate-700 dark:text-slate-300">
                      {task.objective}
                    </span>
                  </li>
                ))}
              </ul>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
