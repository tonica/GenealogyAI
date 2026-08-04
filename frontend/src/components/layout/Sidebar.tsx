import { NavLink } from 'react-router-dom'
import {
  BeakerIcon,
  ClipboardDocumentCheckIcon,
  HomeIcon,
  MagnifyingGlassIcon,
  UserGroupIcon,
  UsersIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline'
import { cn } from '@/utils/cn'

const NAV_ITEMS = [
  { to: '/', label: 'Inici', icon: HomeIcon, end: true },
  { to: '/search', label: 'Cerca', icon: MagnifyingGlassIcon },
  { to: '/statistics', label: 'Estadístiques', icon: ChartBarIcon },
  { to: '/quality', label: 'Qualitat', icon: ClipboardDocumentCheckIcon },
  { to: '/research', label: 'Recerca', icon: BeakerIcon },
]

interface SidebarProps {
  open: boolean
  onClose: () => void
}

export function Sidebar({ open, onClose }: SidebarProps) {
  return (
    <>
      {open && (
        <div
          className="fixed inset-0 z-30 bg-slate-900/50 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-40 w-64 transform border-r border-slate-200 bg-white transition-transform duration-200 lg:static lg:translate-x-0 dark:border-slate-700 dark:bg-slate-900',
          open ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        <div className="flex h-16 items-center gap-2.5 border-b border-slate-200 px-5 dark:border-slate-700">
          <UserGroupIcon className="size-7 text-brand-600 dark:text-brand-400" />
          <div>
            <p className="text-sm font-bold text-slate-900 dark:text-slate-100">
              GenealogyAI
            </p>
            <p className="text-[11px] text-slate-400">Gestió de l'arbre familiar</p>
          </div>
        </div>
        <nav className="flex-1 space-y-1 p-3">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              onClick={onClose}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-brand-50 text-brand-700 dark:bg-brand-900/40 dark:text-brand-200'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-slate-100',
                )
              }
            >
              <item.icon className="size-5" />
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-slate-200 p-4 text-xs text-slate-400 dark:border-slate-700">
          <UsersIcon className="mb-1 inline size-4" /> Arbre genealògic v0.2
        </div>
      </aside>
    </>
  )
}
