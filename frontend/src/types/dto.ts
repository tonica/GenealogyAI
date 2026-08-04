// Tipus alineats amb els DTOs del contracte públic v1 (backend/app/schemas/dto.py).
// No s'haurien de desviar del contracte sense actualitzar també el backend.

export interface PersonSummary {
  id: number
  xref: string | null
  given_name: string | null
  surname: string | null
  prefix: string | null
  suffix: string | null
  sex: 'M' | 'F' | 'U' | null
  display_name: string
  birth_date: string | null
  death_date: string | null
  birth_year: number | null
  death_year: number | null
  birth_place: string | null
  death_place: string | null
  quality: number | null
}

export interface TimelineEvent {
  id: number | null
  event_type: string | null
  date_text: string | null
  date_iso: string | null
  date_year: number | null
  place: string | null
  place_id: number | null
  description: string | null
  sort_year: number | null
}

export interface QualityFactor {
  name: string
  contribution: number
  weight: number
  reason: string
  direction: string
}

export interface PersonQuality {
  person_id: number | null
  xref: string | null
  score: number
  missing: string[]
  issues: string[]
  factors: QualityFactor[]
}

export interface Spouse {
  family_id: number
  spouse: PersonSummary | null
  marriage_date: string | null
  marriage_place: string | null
}

export interface DuplicatePerson {
  id: number | null
  xref: string | null
  name: string
}

export interface DuplicateCandidate {
  person_a: DuplicatePerson
  person_b: DuplicatePerson
  score: number
  confidence: number
  rules_used: string[]
  reasons: string[]
}

export interface ResearchTask {
  person_id: number | null
  xref: string | null
  objective: string
  kind: string
  hypothesis: string | null
  related_person_ids: number[]
  status: 'open' | 'in_progress' | 'done'
  priority: 'high' | 'medium' | 'low'
}

export interface Source {
  id: number | null
  xref: string | null
  title: string
  author: string | null
  publication: string | null
  url: string | null
  citation: string | null
}

export interface PersonDetails extends PersonSummary {
  notes: string | null
  birth: TimelineEvent | null
  death: TimelineEvent | null
  parents: PersonSummary[]
  spouses: Spouse[]
  children: PersonSummary[]
  events: TimelineEvent[]
  timeline: TimelineEvent[]
  quality_detail: PersonQuality | null
  duplicates: DuplicateCandidate[]
  tasks: ResearchTask[]
  sources: Source[]
}

export interface Family {
  id: number
  xref: string | null
  father: PersonSummary | null
  mother: PersonSummary | null
  children: PersonSummary[]
  marriage_date: string | null
  marriage_place: string | null
  events: TimelineEvent[]
}

export interface Statistics {
  persons: number
  families: number
  sources: number
  media: number
  events: number
  males: number
  females: number
  average_age: number | null
  max_age: number | null
  events_by_type: Record<string, number>
  sex_by: Record<string, number>
  surname_frequency: Record<string, number>
  persons_without_name: number
  persons_without_data: number
  birth_year_range: (number | null)[]
  births_by_year: Record<string, number>
  deaths_by_year: Record<string, number>
  top_places: { name: string; count: number }[]
  top_surnames: { surname: string; count: number }[]
  largest_branches: number[]
}

export interface QualityFinding {
  category: string
  severity: 'error' | 'warning' | 'info'
  message: string
  ref: string | null
  metadata: Record<string, unknown>
}

export interface QualityReport {
  total: number
  errors: QualityFinding[]
  warnings: QualityFinding[]
  infos: QualityFinding[]
}

export interface Dashboard {
  persons: number
  families: number
  events: number
  places: number
  sources: number
  media: number
  males: number
  females: number
  average_age: number | null
  average_quality: number | null
  duplicates: number
  pending_tasks: number
  last_import: string | null
}

export interface PersonSearchParams {
  q?: string
  given_name?: string
  surname?: string
  sex?: 'M' | 'F' | 'U'
  place?: string
  birth_year?: number
  limit?: number
  offset?: number
}
