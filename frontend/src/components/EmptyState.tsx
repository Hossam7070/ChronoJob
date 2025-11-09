import { LucideIcon } from 'lucide-react'
import { Link } from 'react-router-dom'

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
  actionLabel?: string
  actionLink?: string
}

const EmptyState = ({
  icon: Icon,
  title,
  description,
  actionLabel,
  actionLink,
}: EmptyStateProps) => {
  return (
    <div className="text-center py-12 bg-white rounded-lg shadow">
      <Icon className="mx-auto h-12 w-12 text-gray-400" />
      <h3 className="mt-2 text-sm font-medium text-gray-900">{title}</h3>
      <p className="mt-1 text-sm text-gray-500">{description}</p>
      {actionLabel && actionLink && (
        <div className="mt-6">
          <Link
            to={actionLink}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
          >
            {actionLabel}
          </Link>
        </div>
      )}
    </div>
  )
}

export default EmptyState
