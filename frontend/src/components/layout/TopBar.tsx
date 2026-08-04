import { Bars3Icon, SunIcon, MoonIcon } from '@heroicons/react/24/outline'
import { cn } from '@/utils/cn'
import type { Theme } from '@/hooks/use-theme'

interface TopBarProps {
  onOpenSidebar: () => void
  theme: Theme
  onToggleTheme: () => void
  title?: string
}

export function TopBar({ onOpenSidebar, theme, onToggleTheme, title }: TopBarProps) {
  return (
    <header className="flex h-16 items-center gap-4 border-b border-slate-200 bg-white px-4 dark:border-slate-700 dark:bg-slate-900">
      <button
        type="button"
        onClick={onOpenSidebar}
        aria-label="Obre el menú"
        className="rounded-md p-2 text-slate-500 hover:bg-slate-100 lg:hidden dark:hover:bg-slate-800"
      >
        <Bars3Icon className="size-6" />
      </button>
      <div className="min-w-0 flex-1">
        {title && (
          <h1 className="truncate text-base font-semibold text-slate-900 dark:text-slate-100">
            {title}
          </h1>
        )}
      </div>
      <button
        type="button"
        onClick={onToggleTheme}
        aria-label={theme === 'dark' ? 'Mode clar' : 'Mode fosc'}
        className={cn(
          'rounded-md p-2 text-slate-500 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800',
        )}
      >
        {theme === 'dark' ? (
          <SunIcon className="size-5" />
        ) : (
          <MoonIcon className="size-5" />
        )}
      </button>
    </header>
  )
}
