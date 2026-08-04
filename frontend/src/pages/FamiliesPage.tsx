import { Link } from 'react-router-dom'
import { useFamilies } from '@/hooks/queries'
import { Card } from '@/components/ui/Card'
import { Loading } from '@/components/ui/Loading'
import { EmptyState } from '@/components/ui/EmptyState'
import { Breadcrumbs } from '@/components/layout/Breadcrumbs'
import { formatLifespan } from '@/utils/format'

export function FamiliesPage() {
  const { data, isLoading, isError } = useFamilies(100, 0)

  if (isLoading) return <Loading full label="Carregant les famílies…" />

  if (isError || !data) {
    return (
      <>
        <Breadcrumbs items={[{ label: 'Inici', to: '/' }, { label: 'Famílies' }]} />
        <Card>
          <EmptyState
            title="No s'han pogut carregar les famílies"
            description="Comprova que el backend estigui en marxa."
          />
        </Card>
      </>
    )
  }

  return (
    <div className="space-y-6">
      <Breadcrumbs items={[{ label: 'Inici', to: '/' }, { label: 'Famílies' }]} />
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">Famílies</h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          {data.length} famílies registrades.
        </p>
      </div>

      {data.length === 0 ? (
        <Card>
          <EmptyState title="Cap família" description="Importa un GEDCOM per començar." />
        </Card>
      ) : (
        <ul className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {data.map((family) => {
            const name =
              [family.father?.display_name, family.mother?.display_name]
                .filter(Boolean)
                .join(' + ') || `Família ${family.id}`
            return (
              <li key={family.id}>
                <Link
                  to={`/families/${family.id}`}
                  className="block rounded-xl border border-slate-200 bg-white p-5 transition-colors hover:border-brand-400 hover:bg-brand-50 dark:border-slate-700 dark:bg-slate-800 dark:hover:bg-slate-800"
                >
                  <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                    {name}
                  </p>
                  <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                    {family.father
                      ? formatLifespan(family.father.birth_year, family.father.death_year)
                      : ''}
                    {family.father && family.mother ? ' · ' : ''}
                    {family.mother
                      ? formatLifespan(family.mother.birth_year, family.mother.death_year)
                      : ''}
                  </p>
                  <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                    {family.children.length} fills
                    {family.marriage_date ? ` · casats el ${family.marriage_date}` : ''}
                  </p>
                </Link>
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}
