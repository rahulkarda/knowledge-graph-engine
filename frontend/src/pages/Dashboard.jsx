import { useNodes } from '../api/hooks/useNodes'
import { useDiscoveredConnections } from '../api/hooks/useGraph'
import { TagPill, LoadingSpinner, EmptyState } from '../components/shared'
import { Link } from 'react-router-dom'
import { FileText, Globe, Mic, File, Network, PlusCircle } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

const TYPE_ICON = {
  note: FileText,
  url: Globe,
  audio: Mic,
  pdf: File,
  docx: File,
  txt: File,
}

const TYPE_COLOR = {
  note: '#6366f1',
  url: '#0ea5e9',
  audio: '#f59e0b',
  pdf: '#ef4444',
  docx: '#10b981',
  txt: '#8b5cf6',
}

function NodeCard({ node }) {
  const Icon = TYPE_ICON[node.content_type] || FileText
  const color = TYPE_COLOR[node.content_type] || '#6366f1'
  return (
    <Link to={`/nodes/${node.id}`} className="card hover:border-gray-600 transition-colors block">
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg shrink-0" style={{ backgroundColor: color + '22' }}>
          <Icon size={16} style={{ color }} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-gray-100 font-medium text-sm truncate">{node.title}</p>
          <p className="text-gray-500 text-xs mt-0.5">
            {formatDistanceToNow(new Date(node.created_at), { addSuffix: true })}
            {node.word_count ? ` · ${node.word_count} words` : ''}
          </p>
          {node.tags?.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {node.tags.slice(0, 3).map((t) => <TagPill key={t.id} tag={t} />)}
            </div>
          )}
        </div>
      </div>
    </Link>
  )
}

export default function Dashboard() {
  const { data: nodes, isLoading } = useNodes({ limit: 10 })
  const { data: connections } = useDiscoveredConnections()

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-100">Dashboard</h1>
          <p className="text-gray-500 text-sm mt-1">Your personal knowledge graph</p>
        </div>
        <Link to="/capture" className="btn-primary flex items-center gap-2">
          <PlusCircle size={16} />
          Capture
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Total Nodes', value: nodes?.length ?? '—' },
          { label: 'Connections', value: connections?.length ?? '—' },
          { label: 'Types', value: nodes ? new Set(nodes.map(n => n.content_type)).size : '—' },
          { label: 'This Week', value: nodes ? nodes.filter(n => {
            const d = new Date(n.created_at)
            return Date.now() - d.getTime() < 7 * 86400000
          }).length : '—' },
        ].map(stat => (
          <div key={stat.label} className="card text-center">
            <p className="text-2xl font-bold text-brand-500">{stat.value}</p>
            <p className="text-gray-500 text-xs mt-1">{stat.label}</p>
          </div>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Recent nodes */}
        <section>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-gray-300 font-semibold">Recent Captures</h2>
            <Link to="/timeline" className="text-brand-500 text-xs hover:underline">View all</Link>
          </div>
          {isLoading ? (
            <div className="flex justify-center py-8"><LoadingSpinner /></div>
          ) : nodes?.length === 0 ? (
            <EmptyState
              icon={FileText}
              title="No notes yet"
              description="Capture your first note to get started."
              action={<Link to="/capture" className="btn-primary text-sm">Capture now</Link>}
            />
          ) : (
            <div className="space-y-2">
              {nodes?.map((n) => <NodeCard key={n.id} node={n} />)}
            </div>
          )}
        </section>

        {/* Discovered connections */}
        <section>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-gray-300 font-semibold">Discovered Connections</h2>
            <Link to="/connections" className="text-brand-500 text-xs hover:underline">View all</Link>
          </div>
          {!connections?.length ? (
            <EmptyState
              icon={Network}
              title="No connections yet"
              description="Add more notes to discover hidden links."
            />
          ) : (
            <div className="space-y-2">
              {connections.slice(0, 5).map((c) => (
                <div key={c.edge_id} className="card">
                  <p className="text-gray-100 text-sm font-medium">
                    {c.source.title} <span className="text-gray-500 font-normal">↔</span> {c.target.title}
                  </p>
                  {c.evidence && <p className="text-gray-500 text-xs mt-1">{c.evidence}</p>}
                  <span className="inline-block mt-2 text-xs px-2 py-0.5 rounded-full bg-brand-600/20 text-brand-400">
                    {(c.strength * 100).toFixed(0)}% match
                  </span>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  )
}
