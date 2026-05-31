export function LoadingSpinner({ size = 'md' }) {
  const s = size === 'sm' ? 'w-4 h-4' : size === 'lg' ? 'w-10 h-10' : 'w-6 h-6'
  return (
    <div className={`${s} border-2 border-brand-500 border-t-transparent rounded-full animate-spin`} />
  )
}

export function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      {Icon && <Icon size={40} className="text-gray-600 mb-4" />}
      <h3 className="text-gray-300 font-medium text-lg mb-1">{title}</h3>
      {description && <p className="text-gray-500 text-sm mb-4 max-w-sm">{description}</p>}
      {action}
    </div>
  )
}

export function TagPill({ tag }) {
  return (
    <span
      className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
      style={{ backgroundColor: tag.color + '22', color: tag.color, border: `1px solid ${tag.color}44` }}
    >
      {tag.name}
    </span>
  )
}
