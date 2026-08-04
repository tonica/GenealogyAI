// Loading global: barra superior que es mostra mentre hi ha cap consulta
// a la xarxa en curs (TanStack Query `useIsFetching`).

import { useIsFetching } from '@tanstack/react-query'

export function GlobalLoadingBar() {
  const isFetching = useIsFetching()

  if (!isFetching) return null

  return (
    <div className="fixed inset-x-0 top-0 z-50 h-0.5 overflow-hidden bg-transparent">
      <div className="h-full w-1/3 animate-[loading-bar_1s_ease-in-out_infinite] rounded-full bg-brand-500" />
    </div>
  )
}
