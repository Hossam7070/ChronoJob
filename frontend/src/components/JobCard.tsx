import { Clock, Database, Mail, Trash2, Play, Edit } from 'lucide-react'
import { Job } from '../types/job'
import cronstrue from 'cronstrue'

interface JobCardProps {
  job: Job
  isSelected: boolean
  onClick: () => void
  onDelete: () => void
  onTest: () => void
  onEdit: () => void
}

const JobCard = ({ job, isSelected, onClick, onDelete, onTest, onEdit }: JobCardProps) => {
  const getCronDescription = (cronExpression: string) => {
    try {
      return cronstrue.toString(cronExpression)
    } catch {
      return cronExpression
    }
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Never'
    return new Date(dateString).toLocaleString()
  }

  return (
    <div
      className={`bg-white rounded-lg shadow p-6 cursor-pointer transition-all ${
        isSelected ? 'ring-2 ring-indigo-500' : 'hover:shadow-md'
      }`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900">{job.job_name}</h3>
          <div className="mt-2 space-y-2">
            <div className="flex items-center text-sm text-gray-600">
              <Clock className="h-4 w-4 mr-2 text-gray-400" />
              {getCronDescription(job.schedule_time)}
            </div>
            <div className="flex items-center text-sm text-gray-600">
              <Database className="h-4 w-4 mr-2 text-gray-400" />
              {job.data_source.source_type === 'api' ? 'API' : 'File'}:{' '}
              {job.data_source.location.substring(0, 40)}
              {job.data_source.location.length > 40 && '...'}
            </div>
            <div className="flex items-center text-sm text-gray-600">
              <Mail className="h-4 w-4 mr-2 text-gray-400" />
              {job.consumer_emails.length} recipient
              {job.consumer_emails.length !== 1 ? 's' : ''}
            </div>
          </div>
        </div>
        <div className="ml-4 flex space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation()
              onTest()
            }}
            className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-md transition-colors"
            aria-label="Test job"
            title="Test and download result"
          >
            <Play className="h-5 w-5" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation()
              onEdit()
            }}
            className="p-2 text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
            aria-label="Edit job"
            title="Edit job"
          >
            <Edit className="h-5 w-5" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation()
              onDelete()
            }}
            className="p-2 text-red-600 hover:bg-red-50 rounded-md transition-colors"
            aria-label="Delete job"
          >
            <Trash2 className="h-5 w-5" />
          </button>
        </div>
      </div>
      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500">Last run: {formatDate(job.last_run)}</p>
      </div>
    </div>
  )
}

export default JobCard
