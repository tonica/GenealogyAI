import { createBrowserRouter } from 'react-router-dom'
import { AppLayout } from '@/layouts/AppLayout'
import { DashboardPage } from '@/pages/DashboardPage'
import { SearchPage } from '@/pages/SearchPage'
import { PersonPage } from '@/pages/PersonPage'
import { FamilyPage } from '@/pages/FamilyPage'
import { FamiliesPage } from '@/pages/FamiliesPage'
import { StatisticsPage } from '@/pages/StatisticsPage'
import { QualityPage } from '@/pages/QualityPage'
import { ResearchPage } from '@/pages/ResearchPage'
import { NotFoundPage } from '@/pages/NotFoundPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'search', element: <SearchPage /> },
      { path: 'persons/:personId', element: <PersonPage /> },
      { path: 'families', element: <FamiliesPage /> },
      { path: 'families/:familyId', element: <FamilyPage /> },
      { path: 'statistics', element: <StatisticsPage /> },
      { path: 'quality', element: <QualityPage /> },
      { path: 'research', element: <ResearchPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])
