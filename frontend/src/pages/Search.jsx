import { useState } from 'react'
import { useSearchMutation } from '../api/hooks/useSearch'
import { LoadingSpinner, TagPill } from '../components/shared'
import { Link } from 'react-router-dom'
import { Search as SearchIcon, FileText, Globe, Mic, File } from 'lucide-react'
import { clsx } from 'clsx'

const TYPE_ICON = { note: FileText, url: Globe, audio: Mic, pdf: File, docx: File, txt: File }

export default function Search() {
  const [query, setQuery] = useState('')
  const [semantic, setSemantic] = useState(true)
  const { mutate, data, isPending } = useSearchMutation()

  const doSearch = () => {
    if (!query.trim()) return
    mutate({ query, semantic })
  }

  const results = Array.isArray(data) ? data : data?.results || []

  return (
    <div className="max-w-3xl">
      <h1 className="text-2xl font-bold text-gray-100 mb-6">Search</h1>

      <div className="flex gap-2 mb-4">
        <input
          className="input flex-1"
          placeholder="Search your knowledge base…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && doSearch()}
        />
        <button className="btn-primary flex items-center gap-2 px-5" onClick={doSearch} disabled={isPending || !query.trim()}>
          {isPending ? <LoadingSpinner size="sm" /> : <SearchIcon size={16} />}
        </button>
      </div>

      <label className="flex items-center gap-2 text-sm text-gray-400 mb-6 cursor-pointer select-none">
        <div
          onClick={() => setSemantic(!semantic)}
          className={clsx(
            'w-8 h-4 rounded-full transition-colors relative cursor-pointer',
            semantic ? 'bg-brand-500' : 'bg-gray-700'
          )}
        >
          <div className={clsx('absolute top-0.5 w-3 h-3 bg-white rounded-full transition-all', semantic ? 'left-4' : 'left-0.5')} />
        </div>
        Semantic search (meaning-based)
      </label>

      {results.length > 0 && (
        <div className="space-y-3">
          <p className="text-gray-500 text-sm">{results.length} results for "{query}"</p>
          {results.map((r) => {
            const nodeId = r.node_id
            const Icon = TYPE_ICON[r.content_type] || FileText
            return (
              <Link key={nodeId} to={`/nodes/${nodeId}`} className="card hover:border-gray-600 transition-colors block">
                <div className="flex items-start gap-3">
                  <Icon size={16} className="text-brand-400 mt-0.5 shrink-0" />
                  <div>
                    <p className="text-gray-100 font-medium text-sm">{r.title}</p>
                    <p className="text-gray-500 text-xs mt-1 line-clamp-2">{r.excerpt}</p>
                    {r.score != null && (
                      <span className="mt-2 inline-block text-xs px-2 py-0.5 rounded-full bg-brand-600/20 text-brand-400">
                        {(r.score * 100).toFixed(0)}% match
                      </span>
                    )}
                  </div>
                </div>
              </Link>
            )
          })}
        </div>
      )}
    </div>
  )
}
