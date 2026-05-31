import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Network, PlusCircle, Search, Link2,
  MessageSquare, Clock, Tag, ChevronLeft, ChevronRight,
} from 'lucide-react'
import { useUIStore } from '../../store/uiStore'
import { clsx } from 'clsx'

const NAV = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/capture', icon: PlusCircle, label: 'Capture' },
  { to: '/graph', icon: Network, label: 'Graph' },
  { to: '/search', icon: Search, label: 'Search' },
  { to: '/connections', icon: Link2, label: 'Connections' },
  { to: '/qa', icon: MessageSquare, label: 'Ask AI' },
  { to: '/timeline', icon: Clock, label: 'Timeline' },
  { to: '/tags', icon: Tag, label: 'Tags' },
]

export default function Sidebar() {
  const { sidebarOpen, toggleSidebar } = useUIStore()

  return (
    <aside
      className={clsx(
        'fixed left-0 top-0 h-full bg-gray-900 border-r border-gray-800 flex flex-col z-30 transition-all duration-200',
        sidebarOpen ? 'w-56' : 'w-14'
      )}
    >
      <div className="flex items-center justify-between px-3 py-4 border-b border-gray-800">
        {sidebarOpen && (
          <span className="font-bold text-brand-500 text-sm tracking-wide">KG Engine</span>
        )}
        <button onClick={toggleSidebar} className="btn-ghost ml-auto p-1.5">
          {sidebarOpen ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
        </button>
      </div>

      <nav className="flex-1 py-3 space-y-0.5 px-1.5">
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-2.5 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-brand-600 text-white'
                  : 'text-gray-400 hover:text-gray-100 hover:bg-gray-800'
              )
            }
          >
            <Icon size={18} className="shrink-0" />
            {sidebarOpen && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
