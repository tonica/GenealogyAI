// Utilitats de format per a dates, anys i percentatges.

export function formatYear(year: number | null | undefined): string {
  if (year === null || year === undefined) return '—'
  return String(year)
}

export function formatDate(date: string | null | undefined): string {
  if (!date) return '—'
  return date
}

export function formatLifespan(
  birth: number | string | null | undefined,
  death: number | string | null | undefined,
): string {
  const b = birth !== null && birth !== undefined ? String(birth) : '?'
  const d = death !== null && death !== undefined ? String(death) : '?'
  return `${b} – ${d}`
}

export function formatPercent(value: number | null | undefined): string {
  if (value === null || value === undefined) return '—'
  return `${Math.round(value * 100)}%`
}

export function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined) return '—'
  return new Intl.NumberFormat('ca-ES').format(value)
}

export function formatRelativeTime(iso: string | null | undefined): string {
  if (!iso) return 'Mai'
  const then = new Date(iso).getTime()
  if (Number.isNaN(then)) return iso
  const diffMs = Date.now() - then
  const minutes = Math.floor(diffMs / 60_000)
  if (minutes < 1) return 'ara mateix'
  if (minutes < 60) return `fa ${minutes} min`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `fa ${hours} h`
  const days = Math.floor(hours / 24)
  if (days < 30) return `fa ${days} dies`
  const months = Math.floor(days / 30)
  if (months < 12) return `fa ${months} mesos`
  const years = Math.floor(months / 12)
  return `fa ${years} anys`
}

export const SEX_LABELS: Record<string, string> = {
  M: 'Home',
  F: 'Dona',
  U: 'Desconegut',
}

export function formatSex(sex: string | null | undefined): string {
  if (!sex) return 'Desconegut'
  return SEX_LABELS[sex] ?? sex
}

export const EVENT_TYPE_LABELS: Record<string, string> = {
  birth: 'Naixement',
  christening: 'Bateig',
  baptism: 'Baptisme',
  death: 'Defunció',
  burial: 'Enterrament',
  marriage: 'Matrimoni',
  divorce: 'Divorci',
  census: 'Padró',
  residence: 'Residència',
  occupation: 'Ocupació',
  immigration: 'Immigració',
  emigration: 'Emigració',
}

export function formatEventType(type: string | null | undefined): string {
  if (!type) return 'Esdeveniment'
  return EVENT_TYPE_LABELS[type] ?? type.replace('_', ' ')
}

export function qualityLabel(score: number | null | undefined): string {
  if (score === null || score === undefined) return '—'
  if (score >= 0.8) return 'Excel·lent'
  if (score >= 0.6) return 'Bona'
  if (score >= 0.4) return 'Regular'
  return 'Baixa'
}
