import { useState, useEffect } from 'react'
import { Clock, RefreshCw, Calendar, Users, CheckCircle } from 'lucide-react'
import { jobsApi } from '../services/api'
import { Job } from '../types/job'
import JobCard from '../components/JobCard'
import JobDetails from '../components/JobDetails'
import StatsCard from '../components/StatsCard'
import ConfirmDialog from '../components/ConfirmDialog'
import EmptyState from '../components/EmptyState'
import LoadingSkeleton from '../components/LoadingSkeleton'
import Alert from '../components/Alert'

const Dashboard = () => {
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedJob, setSelectedJob] = useState<Job | null>(null)
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null)

  const fetchJobs = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await jobsApi.getAllJobs()
      setJobs(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch jobs')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchJobs()
  }, [])

  const handleDelete = async (jobName: string) => {
    try {
      await jobsApi.deleteJob(jobName)
      setJobs(jobs.filter(job => job.job_name !== jobName))
      setDeleteConfirm(null)
      if (selectedJob?.job_name === jobName) {
        setSelectedJob(null)
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete job')
    }
  }

  const getStats = () => {
    const totalJobs = jobs.length
    const jobsWithRuns = jobs.filter((job) => job.last_run).length
    const totalRecipients = jobs.reduce(
      (sum, job) => sum + job.consumer_emails.length,
      0
    )
    return { totalJobs, jobsWithRuns, totalRecipients }
  }

  const stats = getStats()

  if (loading) {
    return (
      <div className="px-4 sm:px-0">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Job Dashboard</h1>
          <p className="mt-2 text-sm text-gray-700">Loading jobs...</p>
        </div>
        <LoadingSkeleton />
      </div>
    )
  }

  return (
    <div className="px-4 sm:px-0">
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Job Dashboard</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage and monitor your scheduled jobs
          </p>
        </div>
        <button
          onClick={fetchJobs}
          className="mt-4 sm:mt-0 inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </button>
      </div>

      {error && (
        <div className="mb-6">
          <Alert
            type="error"
            title="Error"
            message={error}
            onClose={() => setError(null)}
          />
        </div>
      )}

      {jobs.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <StatsCard
            title="Total Jobs"
            value={stats.totalJobs}
            icon={Calendar}
            color="blue"
          />
          <StatsCard
            title="Jobs Executed"
            value={stats.jobsWithRuns}
            icon={CheckCircle}
            color="green"
          />
          <StatsCard
            title="Total Recipients"
            value={stats.totalRecipients}
            icon={Users}
            color="purple"
          />
        </div>
      )}

      {jobs.length === 0 ? (
        <EmptyState
          icon={Clock}
          title="No jobs"
          description="Get started by creating a new scheduled job."
          actionLabel="Create Job"
          actionLink="/create"
        />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-4">
            {jobs.map((job) => (
              <JobCard
                key={job.job_name}
                job={job}
                isSelected={selectedJob?.job_name === job.job_name}
                onClick={() => setSelectedJob(job)}
                onDelete={() => setDeleteConfirm(job.job_name)}
              />
            ))}
          </div>

          <div className="lg:sticky lg:top-6 h-fit">
            <JobDetails job={selectedJob} />
          </div>
        </div>
      )}

      <ConfirmDialog
        isOpen={deleteConfirm !== null}
        title="Confirm Delete"
        message={`Are you sure you want to delete the job "${deleteConfirm}"? This action cannot be undone.`}
        confirmLabel="Delete"
        cancelLabel="Cancel"
        onConfirm={() => deleteConfirm && handleDelete(deleteConfirm)}
        onCancel={() => setDeleteConfirm(null)}
      />
    </div>
  )
}

export default Dashboard
