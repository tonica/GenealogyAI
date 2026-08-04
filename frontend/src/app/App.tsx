import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { RouterProvider } from 'react-router-dom'
import { useState, type ReactNode } from 'react'
import { router } from '@/app/router'
import { NotificationsProvider } from '@/features/notifications/NotificationsProvider'

function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      }),
  )
  return (
    <QueryClientProvider client={queryClient}>
      <NotificationsProvider>{children}</NotificationsProvider>
    </QueryClientProvider>
  )
}

export function App() {
  return (
    <Providers>
      <RouterProvider router={router} />
    </Providers>
  )
}
