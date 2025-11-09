import { Code, Mail } from 'lucide-react'
import { Job } from '../types/job'
import cronstrue from 'cronstrue'

interface JobDetailsProps {
  job: Job | null
}

const JobDetails = ({ job }: JobDetailsProps) => {
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

  if (!job) {
    return (
      <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
        <p>Select a job to view details</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Job Details</h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Job Name
          </label>
          <p className="text-sm text-gray-900">{job.job_name}</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Schedule
          </label>
          <p className="text-sm text-gray-900">{getCronDescription(job.schedule_time)}</p>
          <p className="text-xs text-gray-500 mt-1">Cron: {job.schedule_time}</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Data Source
          </label>
          <p className="text-sm text-gray-900">
            Type: {job.data_source.source_type.toUpperCase()}
            {job.data_source.file_type && ` (${job.data_source.file_type.toUpperCase()})`}
          </p>
          <p className="text-sm text-gray-600 mt-1 break-all">
            {job.data_source.location}
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            <Code className="inline h-4 w-4 mr-1" />
            Processing Script
          </label>
          <pre className="mt-2 p-3 bg-gray-50 rounded-md text-xs text-gray-900 overflow-x-auto">
            {job.processing_script}
          </pre>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Recipients
          </label>
          <ul className="mt-2 space-y-1">
            {job.consumer_emails.map((email, idx) => (
              <li key={idx} className="text-sm text-gray-900 flex items-center">
                <Mail className="h-3 w-3 mr-2 text-gray-400" />
                {email}
              </li>
            ))}
          </ul>
        </div>

        <div className="pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-500">Created: {formatDate(job.created_at)}</p>
          <p className="text-xs text-gray-500 mt-1">
            Last run: {formatDate(job.last_run)}
          </p>
        </div>
      </div>
    </div>
  )
}

export default JobDetails
