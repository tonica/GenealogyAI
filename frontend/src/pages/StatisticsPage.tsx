import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useStatistics } from '@/hooks/queries'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Loading } from '@/components/ui/Loading'
import { EmptyState } from '@/components/ui/EmptyState'
import { formatNumber } from '@/utils/format'

const PIE_COLORS = ['#6366f1', '#a5b4fc', '#22c55e', '#f59e0b', '#ef4444']

export function StatisticsPage() {
  const { data, isLoading, isError } = useStatistics()

  if (isLoading) return <Loading full label="Calculant estadístiques…" />

  if (isError || !data) {
    return (
      <Card>
        <EmptyState
          title="No s'han pogut calcular les estadístiques"
          description="Revisa que el backend estigui disponible."
        />
      </Card>
    )
  }

  const totals = [
    { label: 'Persones', value: data.persons },
    { label: 'Famílies', value: data.families },
    { label: 'Esdeveniments', value: data.events },
    { label: 'Fonts', value: data.sources },
  ]

  const sexData = Object.entries(data.sex_by).map(([name, value]) => ({
    name: name === 'M' ? 'Homes' : name === 'F' ? 'Dones' : 'Desconegut',
    value,
  }))

  const birthData = Object.entries(data.births_by_year)
    .map(([year, count]) => ({ year, naixements: count }))
    .sort((a, b) => Number(a.year) - Number(b.year))

  const deathData = Object.entries(data.deaths_by_year)
    .map(([year, count]) => ({ year, defuncions: count }))
    .sort((a, b) => Number(a.year) - Number(b.year))

  const surnameData = data.top_surnames.map((s) => ({
    name: s.surname,
    persones: s.count,
  }))

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">Estadístiques</h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Resum demogràfic i genealògic del conjunt de dades.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {totals.map((item) => (
          <Card key={item.label} className="p-0">
            <div className="p-5">
              <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                {formatNumber(item.value)}
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400">{item.label}</p>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Distribució per sexe">
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={sexData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={90}
                label
              >
                {sexData.map((_, index) => (
                  <Cell key={index} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Cognoms més freqüents" subtitle="Top 15">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={surnameData} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" allowDecimals={false} />
              <YAxis type="category" dataKey="name" width={90} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="persones" fill="#6366f1" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Naixements per any" subtitle="Distribució temporal">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={birthData} margin={{ left: -10 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="year" tick={{ fontSize: 11 }} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="naixements" fill="#22c55e" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Defuncions per any" subtitle="Distribució temporal">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={deathData} margin={{ left: -10 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="year" tick={{ fontSize: 11 }} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="defuncions" fill="#ef4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card title="Tipus d'esdeveniments">
        <div className="flex flex-wrap gap-2">
          {Object.entries(data.events_by_type).map(([type, count]) => (
            <Badge key={type} tone="neutral">
              {type}: {count}
            </Badge>
          ))}
        </div>
      </Card>
    </div>
  )
}
