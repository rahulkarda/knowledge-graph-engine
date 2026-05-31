import { useParams, Link, useNavigate } from 'react-router-dom'
import { useNode, useNodeNeighbors, useDeleteNode } from '../api/hooks/useNodes'
import { LoadingSpinner, TagPill, EmptyState } from '../components/shared'
import { formatDistanceToNow } from 'date-fns'
import { Trash2, Network, ExternalLink, ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'

export default function NodeDetail() {
  const { id } = useParams()
  const { data: node, isLoading } = useNode(id)
  const { data: neighbors } = useNodeNeighbors(id)
  const { mutate: deleteNode, isPending: deleting } = useDeleteNode()
  const navigate = useNavigate()

  if (isLoading) return <div className="flex justify-center py-20"><LoadingSpinner size="lg" /></div>
  if (!node) return <p className="text-gray-500">Node not found.</p>

  const handleDelete = () => {
    if (!confirm(`Delete "${node.title}"?`)) return
    deleteNode(id, {
      onSuccess: () => { toast.success('Deleted.'); navigate('/dashboard') },
      onError: () => toast.error('Delete failed.'),
    })
  }

  return (
    <div className="max-w-3xl">
      <div className="flex items-center gap-3 mb-6">
        <Link to="/dashboard" className="btn-ghost p-2"><ArrowLeft size={16} /></Link>
        <div className="flex-1">
          <h1 className="text-xl font-bold text-gray-100">{node.title}</h1>
          <p className="text-gray-500 text-xs mt-0.5">
            {node.content_type.toUpperCase()} ·{' '}
            {formatDistanceToNow(new Date(node.created_at), { addSuffix: true })}
            {node.word_count ? ` · ${node.word_count} words` : ''}
          </p>
        </div>
        <button className="btn-ghost text-red-400 hover:text-red-300 p-2" onClick={handleDelete} disabled={deleting}>
          <Trash2 size={16} />
        </button>
      </div>

      {/* Tags */}
      {node.tags?.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-4">
          {node.tags.map(t => <TagPill key={t.id} tag={t} />)}
        </div>
      )}

      {/* Content */}
      <div className="card mb-6">
        <pre className="text-gray-300 text-sm whitespace-pre-wrap font-sans leading-relaxed">{node.content}</pre>
      </div>

      {/* Source URL */}
      {node.source_url && (
        <a href={node.source_url} target="_blank" rel="noopener noreferrer"
          className="flex items-center gap-2 text-brand-400 text-sm hover:underline mb-6">
          <ExternalLink size={14} />
          {node.source_url}
        </a>
      )}

      {/* Entities */}
      {node.entities?.length > 0 && (
        <section className="mb-6">
          <h2 className="text-gray-400 font-semibold text-sm mb-2">Extracted Entities</h2>
          <div className="flex flex-wrap gap-1.5">
            {node.entities.map(e => (
              <span key={e.id} className="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-300 border border-gray-700">
                <span className="text-gray-500 mr-1">{e.entity_type}</span>{e.name}
              </span>
            ))}
          </div>
        </section>
      )}

      {/* Neighbors */}
      {neighbors?.length > 0 && (
        <section>
          <h2 className="text-gray-400 font-semibold text-sm mb-2 flex items-center gap-2">
            <Network size={14} /> Connected Nodes ({neighbors.length})
          </h2>
          <div className="grid grid-cols-2 gap-2">
            {neighbors.map(n => (
              <Link key={n.id} to={`/nodes/${n.id}`} className="card hover:border-gray-600 transition-colors !p-3">
                <p className="text-gray-100 text-sm font-medium truncate">{n.title}</p>
                <p className="text-gray-500 text-xs capitalize mt-0.5">{n.content_type}</p>
              </Link>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
