import { forwardRef, type InputHTMLAttributes } from 'react'
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline'
import { cn } from '@/utils/cn'

export const SearchBox = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => {
    return (
      <div className={cn('relative', className)}>
        <MagnifyingGlassIcon className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400" />
        <input
          ref={ref}
          type="search"
          className="w-full rounded-lg border border-slate-300 bg-white py-2 pl-9 pr-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
          {...props}
        />
      </div>
    )
  },
)
SearchBox.displayName = 'SearchBox'
