import { UserCircleIcon } from '@heroicons/react/24/outline'
import type { PersonDetails } from '@/types/dto'
import { formatLifespan, formatSex } from '@/utils/format'

interface PersonCardProps {
  person: PersonDetails
}

export function PersonCard({ person }: PersonCardProps) {
  return (
    <div className="flex flex-col items-center gap-3 rounded-xl border border-slate-200 bg-white p-6 text-center dark:border-slate-700 dark:bg-slate-800">
      <UserCircleIcon className="size-20 text-slate-300 dark:text-slate-600" />
      <div>
        <p className="text-lg font-semibold text-slate-900 dark:text-slate-100">
          {person.display_name}
        </p>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          {formatSex(person.sex)}
        </p>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
          {formatLifespan(person.birth_date, person.death_date)}
        </p>
      </div>
    </div>
  )
}
