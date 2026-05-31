import { useTags } from '../api/hooks/useTags'
import { LoadingSpinner, EmptyState } from '../components/shared'
import { Tag } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Tags() {
  const { data: tags, isLoading } = useTags()

  if (isLoading) return <div className="flex justify-center py-20"><LoadingSpinner size="lg" /></div>

  return (
    <div className="max-w-3xl">
      <h1 className="text-2xl font-bold text-gray-100 mb-6">Tags</h1>

      {!tags?.length ? (
        <EmptyState icon={Tag} title="No tags yet" description="Tags are auto-generated when you capture notes." />
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {tags.map(tag => (
            <Link key={tag.id} to={`/dashboard?tag_id=${tag.id}`}
              className="card hover:border-gray-600 transition-colors flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: tag.color }} />
                <span className="text-gray-200 text-sm font-medium">{tag.name}</span>
              </div>
              <span className="text-gray-500 text-xs">{tag.node_count}</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
