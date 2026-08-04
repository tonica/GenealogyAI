// Hook d'accés al sistema de notificacions global.

import { createContext, useContext } from 'react'

export type NotificationsTone = 'success' | 'error' | 'info'

export interface NotificationsContextValue {
  notify: (title: string, opts?: { tone?: NotificationsTone; description?: string }) => void
  success: (title: string, description?: string) => void
  error: (title: string, description?: string) => void
  info: (title: string, description?: string) => void
}

export const NotificationsContext = createContext<NotificationsContextValue | null>(null)

export function useNotifications(): NotificationsContextValue {
  const ctx = useContext(NotificationsContext)
  if (!ctx) {
    throw new Error('useNotifications must be used within NotificationsProvider')
  }
  return ctx
}
