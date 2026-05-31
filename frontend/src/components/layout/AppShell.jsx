import Sidebar from './Sidebar'
import { useUIStore } from '../../store/uiStore'
import { clsx } from 'clsx'

export default function AppShell({ children }) {
  const sidebarOpen = useUIStore((s) => s.sidebarOpen)

  return (
    <div className="flex h-screen overflow-hidden bg-gray-950">
      <Sidebar />
      <main
        className={clsx(
          'flex-1 overflow-y-auto transition-all duration-200',
          sidebarOpen ? 'ml-56' : 'ml-14'
        )}
      >
        <div className="max-w-7xl mx-auto px-6 py-6">{children}</div>
      </main>
    </div>
  )
}
