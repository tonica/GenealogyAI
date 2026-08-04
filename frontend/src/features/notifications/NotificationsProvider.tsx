// Sistema de notificacions global: context + render de toasts.

import {
  useCallback,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react'
import { CheckCircleIcon, InformationCircleIcon, XCircleIcon, XMarkIcon } from '@heroicons/react/24/outline'
import { cn } from '@/utils/cn'
import {
  NotificationsContext,
  type NotificationsContextValue,
  type NotificationsTone,
} from '@/features/notifications/use-notifications'

interface Toast {
  id: number
  tone: NotificationsTone
  title: string
  description?: string
}

const TONE_STYLES: Record<NotificationsTone, string> = {
  success: 'border-emerald-200 text-emerald-700 dark:border-emerald-800 dark:text-emerald-300',
  error: 'border-red-200 text-red-700 dark:border-red-800 dark:text-red-300',
  info: 'border-sky-200 text-sky-700 dark:border-sky-800 dark:text-sky-300',
}

const TONE_ICONS: Record<NotificationsTone, typeof InformationCircleIcon> = {
  success: CheckCircleIcon,
  error: XCircleIcon,
  info: InformationCircleIcon,
}

export function NotificationsProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])
  const nextId = useRef(1)

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const notify = useCallback(
    (title: string, opts: { tone?: NotificationsTone; description?: string } = {}) => {
      const id = nextId.current++
      setToasts((prev) => [...prev, { id, tone: opts.tone ?? 'info', title, description: opts.description }])
      window.setTimeout(() => dismiss(id), 5000)
    },
    [dismiss],
  )

  const value = useMemo<NotificationsContextValue>(
    () => ({
      notify,
      success: (title, description) => notify(title, { tone: 'success', description }),
      error: (title, description) => notify(title, { tone: 'error', description }),
      info: (title, description) => notify(title, { tone: 'info', description }),
    }),
    [notify],
  )

  return (
    <NotificationsContext.Provider value={value}>
      {children}
      <div
        aria-live="polite"
        className="pointer-events-none fixed bottom-4 right-4 z-50 flex w-full max-w-sm flex-col gap-2"
      >
        {toasts.map((toast) => {
          const Icon = TONE_ICONS[toast.tone]
          return (
            <div
              key={toast.id}
              role="status"
              className={cn(
                'pointer-events-auto flex items-start gap-3 rounded-lg border bg-white p-3 shadow-lg dark:bg-slate-900',
                TONE_STYLES[toast.tone],
              )}
            >
              <Icon className="mt-0.5 size-5 shrink-0" />
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold">{toast.title}</p>
                {toast.description && (
                  <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
                    {toast.description}
                  </p>
                )}
              </div>
              <button
                type="button"
                aria-label="Tanca la notificació"
                onClick={() => dismiss(toast.id)}
                className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800"
              >
                <XMarkIcon className="size-4" />
              </button>
            </div>
          )
        })}
      </div>
    </NotificationsContext.Provider>
  )
}
