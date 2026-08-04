import { useState } from 'react'
import { useQualityReport } from '@/hooks/queries'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Table } from '@/components/ui/Table'
import { Loading } from '@/components/ui/Loading'
import { EmptyState } from '@/components/ui/EmptyState'
import { Button } from '@/components/ui/Button'
import type { QualityFinding } from '@/types/dto'

type Tab = 'errors' | 'warnings' | 'infos'

export function QualityPage() {
  const { data, isLoading, isError } = useQualityReport()
  const [tab, setTab] = useState<Tab>('errors')

  if (isLoading) return <Loading full label="Generant l'informe de qualitat…" />

  if (isError || !data) {
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
    errors: data.errors.length,
    warnings: data.warnings.length,
    infos: data.infos.length,
  }

  const tabs: Tab[] = ['errors', 'warnings', 'infos']

  const current: QualityFinding[] = data[tab]

  const columns = [
    { key: 'severity', header: 'Severitat' },
    { key: 'category', header: 'Categoria' },
    { key: 'ref', header: 'Referència' },
    { key: 'message', header: 'Observació' },
  ]

  const rows = current.map((f) => [
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

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">
          Qualitat de les dades
        </h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          {data.total} observacions detectades al conjunt de dades.
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
            {t === 'errors' ? 'Errors' : t === 'warnings' ? 'Avisos' : 'Informació'} (
            {counts[t]})
          </Button>
        ))}
      </div>

      <Card>
        {current.length === 0 ? (
          <EmptyState title="Cap observació en aquesta categoria" />
        ) : (
          <Table columns={columns} rows={rows} />
        )}
      </Card>
    </div>
  )
}
