import { useTimeline } from '../api/hooks/useTags'
import { LoadingSpinner, TagPill, EmptyState } from '../components/shared'
import { Link } from 'react-router-dom'
import { Clock, FileText, Globe, Mic, File } from 'lucide-react'
import { format } from 'date-fns'

const TYPE_ICON = { note: FileText, url: Globe, audio: Mic, pdf: File, docx: File, txt: File }

export default function Timeline() {
  const { data: groups, isLoading } = useTimeline(50)

  if (isLoading) return <div className="flex justify-center py-20"><LoadingSpinner size="lg" /></div>

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-100 mb-6">Timeline</h1>

      {!groups?.length ? (
        <EmptyState icon={Clock} title="Nothing captured yet" description="Your knowledge timeline will appear here." />
      ) : (
        <div className="space-y-8">
          {groups.map(group => (
            <div key={group.date}>
              <h2 className="text-gray-500 text-xs font-semibold uppercase tracking-wider mb-3">
                {format(new Date(group.date), 'EEEE, MMMM d, yyyy')}
              </h2>
              <div className="space-y-2 border-l-2 border-gray-800 pl-4">
                {group.items.map(item => {
                  const Icon = TYPE_ICON[item.content_type] || FileText
                  return (
                    <Link key={item.id} to={`/nodes/${item.id}`} className="card hover:border-gray-600 transition-colors block">
                      <div className="flex items-start gap-3">
                        <Icon size={15} className="text-gray-500 mt-0.5 shrink-0" />
                        <div className="flex-1 min-w-0">
                          <p className="text-gray-100 text-sm font-medium truncate">{item.title}</p>
                          <p className="text-gray-500 text-xs mt-0.5 line-clamp-1">{item.excerpt}</p>
                          {item.tags?.length > 0 && (
                            <div className="flex gap-1 flex-wrap mt-1.5">
                              {item.tags.slice(0, 3).map(t => <TagPill key={t.id} tag={t} />)}
                            </div>
                          )}
                        </div>
                        <span className="text-gray-600 text-xs shrink-0">
                          {format(new Date(item.created_at), 'HH:mm')}
                        </span>
                      </div>
                    </Link>
                  )
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
