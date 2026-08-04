import { Link } from 'react-router-dom'
import { EmptyState } from '@/components/ui/EmptyState'

export function NotFoundPage() {
  return (
    <div className="flex items-center justify-center py-24">
      <EmptyState
        title="Pàgina no trobada"
        description="La ruta no existeix o s'ha mogut."
        action={
          <Link to="/" className="text-sm font-medium text-brand-600 hover:underline">
            Torna a l'inici
          </Link>
        }
      />
    </div>
  )
}
