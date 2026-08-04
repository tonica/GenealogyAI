import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Sidebar } from '@/components/layout/Sidebar'
import { TopBar } from '@/components/layout/TopBar'
import { GlobalLoadingBar } from '@/components/layout/GlobalLoadingBar'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { useTheme } from '@/theme/use-theme'

export function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { theme, toggle } = useTheme()

  return (
    <div className="flex min-h-screen bg-slate-50 dark:bg-slate-950">
      <GlobalLoadingBar />
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar
          onOpenSidebar={() => setSidebarOpen(true)}
          theme={theme}
          onToggleTheme={toggle}
        />
        <main className="flex-1 p-4 lg:p-6">
          <ErrorBoundary>
            <Outlet />
          </ErrorBoundary>
        </main>
      </div>
    </div>
  )
}
