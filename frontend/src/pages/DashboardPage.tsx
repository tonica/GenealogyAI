import { Link } from 'react-router-dom'
import {
  UsersIcon,
  UserGroupIcon,
  CalendarDaysIcon,
  ClipboardDocumentCheckIcon,
  BeakerIcon,
  ArrowPathRoundedSquareIcon,
} from '@heroicons/react/24/outline'
import { useDashboard } from '@/hooks/queries'
import { Card } from '@/components/ui/Card'
import { Loading } from '@/components/ui/Loading'
import { Badge } from '@/components/ui/Badge'
import { EmptyState } from '@/components/ui/EmptyState'
import { formatNumber, formatRelativeTime } from '@/utils/format'

export function DashboardPage() {
  const { data, isLoading, isError } = useDashboard()

  if (isLoading) return <Loading full label="Carregant el resum…" />

  if (isError || !data) {
    return (
      <Card>
        <EmptyState
          title="No s'ha pogut carregar el resum"
          description="Comprova que el backend estigui en marxa i que la base de dades tingui dades importades."
        />
      </Card>
    )
  }

  const stats = [
    { label: 'Persones', value: data.persons, icon: UsersIcon },
    { label: 'Famílies', value: data.families, icon: UserGroupIcon },
    { label: 'Esdeveniments', value: data.events, icon: CalendarDaysIcon },
    { label: 'Llocs', value: data.places, icon: ArrowPathRoundedSquareIcon },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">Inici</h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Resum del teu arbre genealògic i de les tasques pendents.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label} className="p-0">
            <div className="flex items-center gap-4 p-5">
              <div className="flex size-11 items-center justify-center rounded-lg bg-brand-50 text-brand-600 dark:bg-brand-900/40 dark:text-brand-300">
                <stat.icon className="size-6" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                  {formatNumber(stat.value)}
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400">{stat.label}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card
          title="Qualitat de les dades"
          subtitle="Puntuació mitjana de completesa"
        >
          <div className="flex flex-col gap-3">
            <div className="text-4xl font-bold text-slate-900 dark:text-slate-100">
              {data.average_quality !== null ? `${Math.round(data.average_quality * 100)}%` : '—'}
            </div>
            <div className="flex items-center gap-2">
              <Badge tone={data.duplicates > 0 ? 'warning' : 'success'}>
                {formatNumber(data.duplicates)} possibles duplicats
              </Badge>
            </div>
            <Link
              to="/quality"
              className="text-sm font-medium text-brand-600 hover:text-brand-700 dark:text-brand-400"
            >
              Revisar l'informe →
            </Link>
          </div>
        </Card>

        <Card title="Tasques de recerca" subtitle="Suggeriments pendents d'investigar">
          <div className="flex flex-col gap-3">
            <div className="flex items-center gap-3">
              <BeakerIcon className="size-8 text-brand-500" />
              <div className="text-4xl font-bold text-slate-900 dark:text-slate-100">
                {formatNumber(data.pending_tasks)}
              </div>
            </div>
            <Link
              to="/research"
              className="text-sm font-medium text-brand-600 hover:text-brand-700 dark:text-brand-400"
            >
              Veure suggeriments →
            </Link>
          </div>
        </Card>

        <Card title="Darrera importació" subtitle="Origen de les dades actuals">
          <div className="flex flex-col gap-3">
            <Badge tone="neutral">{formatRelativeTime(data.last_import)}</Badge>
            <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
              <UsersIcon className="size-4" />
              {data.males} homes · {data.females} dones
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
              <ClipboardDocumentCheckIcon className="size-4" />
              Edat mitjana: {data.average_age !== null ? data.average_age : '—'} anys
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
