import { useDiscoveredConnections } from '../api/hooks/useGraph'
import { LoadingSpinner, EmptyState } from '../components/shared'
import { Link } from 'react-router-dom'
import { Link2 } from 'lucide-react'
import client from '../api/client'
import { useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'

export default function Connections() {
  const { data: connections, isLoading } = useDiscoveredConnections()
  const qc = useQueryClient()

  const accept = async (c) => {
    try {
      await client.post('/graph/edges', {
        source_node_id: c.source.id,
        target_node_id: c.target.id,
        relationship: c.relationship,
        evidence: c.evidence,
      })
      toast.success('Connection accepted.')
      qc.invalidateQueries({ queryKey: ['graph'] })
    } catch { toast.error('Failed.') }
  }

  if (isLoading) return <div className="flex justify-center py-20"><LoadingSpinner size="lg" /></div>

  return (
    <div className="max-w-3xl">
      <h1 className="text-2xl font-bold text-gray-100 mb-2">Discovered Connections</h1>
      <p className="text-gray-500 text-sm mb-6">Non-obvious links found between your notes.</p>

      {!connections?.length ? (
        <EmptyState icon={Link2} title="No connections found" description="Capture more notes to start discovering hidden links between your ideas." />
      ) : (
        <div className="space-y-3">
          {connections.map((c) => (
            <div key={c.edge_id} className="card">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 text-sm">
                    <Link to={`/nodes/${c.source.id}`} className="text-brand-400 hover:underline font-medium">{c.source.title}</Link>
                    <span className="text-gray-600">↔</span>
                    <Link to={`/nodes/${c.target.id}`} className="text-brand-400 hover:underline font-medium">{c.target.title}</Link>
                  </div>
                  {c.evidence && <p className="text-gray-500 text-xs mt-1">{c.evidence}</p>}
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-xs px-2 py-0.5 rounded-full bg-gray-800 text-gray-400">{c.relationship}</span>
                    <span className="text-xs text-gray-500">{(c.strength * 100).toFixed(0)}% confidence</span>
                  </div>
                </div>
                <button onClick={() => accept(c)} className="btn-primary text-xs px-3 py-1.5 shrink-0">Accept</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
