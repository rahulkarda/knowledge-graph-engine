import { useRef, useCallback, useEffect, useState } from 'react'
import { useFullGraph } from '../api/hooks/useGraph'
import { useNode } from '../api/hooks/useNodes'
import { useUIStore } from '../store/uiStore'
import { LoadingSpinner, TagPill } from '../components/shared'
import { Link } from 'react-router-dom'
import ForceGraph2D from 'react-force-graph-2d'
import { X, ExternalLink, Network } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

const TYPE_COLOR = {
  note: '#6366f1',
  url: '#0ea5e9',
  audio: '#f59e0b',
  pdf: '#ef4444',
  docx: '#10b981',
  txt: '#8b5cf6',
}

function NodePanel({ nodeId, onClose }) {
  const { data: node, isLoading } = useNode(nodeId)

  return (
    <div className="absolute top-0 right-0 h-full w-80 bg-gray-900 border-l border-gray-800 flex flex-col z-20 shadow-2xl">
      {/* Header */}
      <div className="flex items-start justify-between p-4 border-b border-gray-800">
        <div className="flex-1 min-w-0 pr-2">
          {isLoading ? (
            <div className="flex items-center gap-2"><LoadingSpinner size="sm" /><span className="text-gray-400 text-sm">Loading…</span></div>
          ) : (
            <>
              <p className="text-gray-100 font-semibold text-sm leading-snug">{node?.title}</p>
              <p className="text-gray-500 text-xs mt-0.5 capitalize">
                {node?.content_type} ·{' '}
                {node?.created_at && formatDistanceToNow(new Date(node.created_at), { addSuffix: true })}
                {node?.word_count ? ` · ${node.word_count}w` : ''}
              </p>
            </>
          )}
        </div>
        <button onClick={onClose} className="btn-ghost p-1.5 shrink-0 text-gray-500 hover:text-gray-100">
          <X size={16} />
        </button>
      </div>

      {/* Body */}
      {!isLoading && node && (
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Tags */}
          {node.tags?.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {node.tags.map(t => <TagPill key={t.id} tag={t} />)}
            </div>
          )}

          {/* Content excerpt */}
          <div>
            <p className="text-gray-500 text-xs font-medium uppercase tracking-wider mb-1.5">Content</p>
            <p className="text-gray-300 text-xs leading-relaxed line-clamp-8">{node.content}</p>
          </div>

          {/* Entities */}
          {node.entities?.length > 0 && (
            <div>
              <p className="text-gray-500 text-xs font-medium uppercase tracking-wider mb-1.5">Entities</p>
              <div className="flex flex-wrap gap-1">
                {node.entities.slice(0, 8).map(e => (
                  <span key={e.id} className="text-xs px-1.5 py-0.5 rounded bg-gray-800 text-gray-300 border border-gray-700">
                    <span className="text-gray-500 mr-1">{e.entity_type}</span>{e.name}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Connected nodes */}
          {(node.outgoing_edges?.length > 0 || node.incoming_edges?.length > 0) && (
            <div>
              <p className="text-gray-500 text-xs font-medium uppercase tracking-wider mb-1.5 flex items-center gap-1">
                <Network size={11} /> Connections
              </p>
              <div className="space-y-1">
                {[...node.outgoing_edges, ...node.incoming_edges].slice(0, 5).map(e => (
                  <div key={e.id} className="text-xs text-gray-400 px-2 py-1 bg-gray-800 rounded">
                    <span className="text-brand-400">{e.rel_type || e.relationship}</span>
                    <span className="text-gray-600 ml-1">· {(e.weight * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Source URL */}
          {node.source_url && (
            <a href={node.source_url} target="_blank" rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-brand-400 text-xs hover:underline truncate">
              <ExternalLink size={11} />
              {node.source_url}
            </a>
          )}
        </div>
      )}

      {/* Footer */}
      {!isLoading && node && (
        <div className="p-4 border-t border-gray-800">
          <Link
            to={`/nodes/${node.id}`}
            className="btn-primary w-full text-center text-sm block"
          >
            Open full page →
          </Link>
        </div>
      )}
    </div>
  )
}

export default function GraphView() {
  const { data, isLoading } = useFullGraph()
  const { setSelectedNodeId, graphFilters } = useUIStore()
  const fgRef = useRef()
  const [tooltip, setTooltip] = useState(null)
  const [selectedId, setSelectedId] = useState(null)
  const [dimensions, setDimensions] = useState({
    width: window.innerWidth - 56,
    height: window.innerHeight,
  })

  useEffect(() => {
    const onResize = () =>
      setDimensions({ width: window.innerWidth - 56, height: window.innerHeight })
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [])

  useEffect(() => {
    if (fgRef.current) {
      fgRef.current.d3Force('charge')?.strength(-120)
      fgRef.current.d3Force('link')?.distance(80)
    }
  }, [data])

  const handleNodeHover = useCallback((node) => {
    if (node) {
      node.fx = node.x
      node.fy = node.y
      setTooltip({ id: node.id, title: node.title, type: node.content_type })
    } else {
      setTooltip(null)
    }
    setTimeout(() => fgRef.current?.cooldownTicks?.(0), 0)
  }, [])

  const handleNodeClick = useCallback((node) => {
    node.fx = node.x
    node.fy = node.y
    setSelectedId(prev => prev === node.id ? null : node.id)
    setSelectedNodeId(node.id)
  }, [setSelectedNodeId])

  const closePanel = useCallback(() => setSelectedId(null), [])

  if (isLoading) {
    return <div className="flex justify-center items-center h-full py-32"><LoadingSpinner size="lg" /></div>
  }

  const filteredNodes = data?.nodes?.filter(n =>
    graphFilters.contentTypes.length === 0 || graphFilters.contentTypes.includes(n.content_type)
  ) || []

  const nodeIds = new Set(filteredNodes.map(n => n.id))
  const filteredLinks = (data?.links || []).filter(l => nodeIds.has(l.source) && nodeIds.has(l.target))

  // Shrink graph width when panel is open
  const graphWidth = selectedId ? dimensions.width - 320 : dimensions.width

  return (
    <div className="relative -mx-6 -my-6 overflow-hidden" style={{ height: dimensions.height }}>
      {data?.nodes?.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full">
          <p className="text-gray-400">
            No nodes yet.{' '}
            <a href="/capture" className="text-brand-500 underline">Capture some knowledge</a> first.
          </p>
        </div>
      ) : (
        <ForceGraph2D
          ref={fgRef}
          graphData={{ nodes: filteredNodes, links: filteredLinks }}
          nodeId="id"
          nodeLabel=""
          nodeColor={(n) => {
            const base = TYPE_COLOR[n.content_type] || '#6366f1'
            return n.id === selectedId ? '#ffffff' : base
          }}
          nodeRelSize={6}
          nodeCanvasObjectMode={() => 'after'}
          nodeCanvasObject={(node, ctx, globalScale) => {
            // Highlight ring for selected node
            if (node.id === selectedId) {
              ctx.beginPath()
              ctx.arc(node.x, node.y, 9, 0, 2 * Math.PI)
              ctx.strokeStyle = '#ffffff'
              ctx.lineWidth = 2 / globalScale
              ctx.stroke()
            }
            if (globalScale < 1.5) return
            const label = node.title.length > 20 ? node.title.slice(0, 20) + '…' : node.title
            const fontSize = 12 / globalScale
            ctx.font = `${fontSize}px Sans-Serif`
            ctx.textAlign = 'center'
            ctx.textBaseline = 'middle'
            ctx.fillStyle = 'rgba(255,255,255,0.85)'
            ctx.fillText(label, node.x, node.y + 10 / globalScale)
          }}
          linkColor={() => '#374151'}
          linkWidth={(l) => Math.max(0.5, (l.weight || 1) * 1.5)}
          onNodeClick={handleNodeClick}
          onNodeHover={handleNodeHover}
          cooldownTicks={100}
          warmupTicks={50}
          backgroundColor="#030712"
          width={graphWidth}
          height={dimensions.height}
          enableNodeDrag={true}
          onNodeDragEnd={(node) => {
            node.fx = node.x
            node.fy = node.y
          }}
        />
      )}

      {/* Hover tooltip */}
      {tooltip && !selectedId && (
        <div className="absolute top-6 left-1/2 -translate-x-1/2 card text-sm pointer-events-none z-10">
          <p className="text-gray-100 font-medium">{tooltip.title}</p>
          <p className="text-gray-500 text-xs capitalize">{tooltip.type}</p>
        </div>
      )}

      {/* Legend */}
      <div className="absolute bottom-6 left-6 card text-xs space-y-1.5 !p-3 z-10">
        {Object.entries(TYPE_COLOR).map(([type, color]) => (
          <div key={type} className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
            <span className="text-gray-400 capitalize">{type}</span>
          </div>
        ))}
      </div>

      {/* Inline detail panel */}
      {selectedId && <NodePanel nodeId={selectedId} onClose={closePanel} />}
    </div>
  )
}
