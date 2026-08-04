import { cn } from '@/utils/cn'

interface LoadingProps {
  label?: string
  className?: string
  full?: boolean
}

export function Loading({ label = 'Carregant…', className, full }: LoadingProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={cn(
        'flex items-center justify-center gap-2 text-slate-500 dark:text-slate-400',
        full && 'flex-1 py-16',
        className,
      )}
    >
      <svg
        className="size-5 animate-spin text-brand-600 dark:text-brand-400"
        viewBox="0 0 24 24"
        fill="none"
        aria-hidden="true"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
        />
      </svg>
      <span className="text-sm">{label}</span>
    </div>
  )
}
