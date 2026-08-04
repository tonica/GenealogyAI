import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { EmptyState } from '@/components/ui/EmptyState'
import { formatEventType } from '@/utils/format'
import type { TimelineEvent } from '@/types/dto'

interface TimelineProps {
  events: TimelineEvent[]
}

export function Timeline({ events }: TimelineProps) {
  const sorted = [...events].sort((a, b) => {
    const ay = a.sort_year ?? a.date_year ?? 9999
    const by = b.sort_year ?? b.date_year ?? 9999
    return ay - by
  })

  if (sorted.length === 0) {
    return <Card title="Línia del temps"><EmptyState title="Sense esdeveniments" /></Card>
  }

  return (
    <Card title="Línia del temps" subtitle="Esdeveniments vitals ordenats cronològicament">
      <ol className="relative ml-3 space-y-6 border-l border-slate-200 dark:border-slate-700">
        {sorted.map((event, index) => (
          <li key={event.id ?? index} className="relative pl-6">
            <span className="absolute -left-[5px] top-1.5 size-2.5 rounded-full bg-brand-500" />
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone="info">{formatEventType(event.event_type)}</Badge>
              <span className="text-sm font-medium text-slate-700 dark:text-slate-200">
                {event.date_year ?? '—'}
              </span>
            </div>
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
              {event.date_text || 'Data desconeguda'}
              {event.place ? ` · ${event.place}` : ''}
            </p>
            {event.description && (
              <p className="mt-0.5 text-xs text-slate-400 dark:text-slate-500">
                {event.description}
              </p>
            )}
          </li>
        ))}
      </ol>
    </Card>
  )
}
