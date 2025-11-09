import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, X } from 'lucide-react'
import { jobsApi } from '../services/api'
import { JobCreate, SourceType, FileType } from '../types/job'
import Alert from '../components/Alert'

const CreateJob = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const [formData, setFormData] = useState<JobCreate>({
    job_name: '',
    schedule_time: '',
    data_source: {
      source_type: 'api',
      location: '',
    },
    processing_script: '',
    consumer_emails: [''],
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(false)

    try {
      const cleanedData = {
        ...formData,
        consumer_emails: formData.consumer_emails.filter(email => email.trim() !== ''),
      }

      await jobsApi.createJob(cleanedData)
      setSuccess(true)
      setTimeout(() => {
        navigate('/dashboard')
      }, 1500)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create job')
    } finally {
      setLoading(false)
    }
  }

  const addEmail = () => {
    setFormData({
      ...formData,
      consumer_emails: [...formData.consumer_emails, ''],
    })
  }

  const removeEmail = (index: number) => {
    setFormData({
      ...formData,
      consumer_emails: formData.consumer_emails.filter((_, i) => i !== index),
    })
  }

  const updateEmail = (index: number, value: string) => {
    const newEmails = [...formData.consumer_emails]
    newEmails[index] = value
    setFormData({ ...formData, consumer_emails: newEmails })
  }

  const cronExamples = [
    { cron: '0 9 * * 1-5', desc: '9 AM, Monday-Friday' },
    { cron: '30 14 * * *', desc: '2:30 PM daily' },
    { cron: '0 */6 * * *', desc: 'Every 6 hours' },
    { cron: '0 0 1 * *', desc: 'First day of month' },
  ]

  const scriptExample = `# Filter and aggregate data
filtered = data[data['amount'] > 100]
result = filtered.groupby('category').agg({
    'amount': 'sum',
    'quantity': 'count'
}).reset_index()`

  return (
    <div className="px-4 sm:px-0">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Create New Job</h1>
        <p className="mt-2 text-sm text-gray-700">
          Configure a new scheduled job for automated data processing
        </p>
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

      {success && (
        <div className="mb-6">
          <Alert
            type="success"
            title="Success"
            message="Job created successfully! Redirecting..."
          />
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
          
          <div className="space-y-4">
            <div>
              <label htmlFor="job_name" className="block text-sm font-medium text-gray-700">
                Job Name *
              </label>
              <input
                type="text"
                id="job_name"
                required
                value={formData.job_name}
                onChange={(e) => setFormData({ ...formData, job_name: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
                placeholder="daily_sales_report"
              />
            </div>

            <div>
              <label htmlFor="schedule_time" className="block text-sm font-medium text-gray-700">
                Schedule (Cron Expression) *
              </label>
              <input
                type="text"
                id="schedule_time"
                required
                value={formData.schedule_time}
                onChange={(e) => setFormData({ ...formData, schedule_time: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
                placeholder="0 9 * * 1-5"
              />
              <div className="mt-2 text-xs text-gray-500">
                <p className="font-medium mb-1">Examples:</p>
                <ul className="space-y-1">
                  {cronExamples.map((ex, idx) => (
                    <li key={idx}>
                      <button
                        type="button"
                        onClick={() => setFormData({ ...formData, schedule_time: ex.cron })}
                        className="text-indigo-600 hover:text-indigo-800"
                      >
                        {ex.cron}
                      </button>
                      {' - '}{ex.desc}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Data Source</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Source Type *
              </label>
              <div className="flex space-x-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="api"
                    checked={formData.data_source.source_type === 'api'}
                    onChange={(e) => setFormData({
                      ...formData,
                      data_source: {
                        source_type: e.target.value as SourceType,
                        location: formData.data_source.location,
                      }
                    })}
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
                  />
                  <span className="ml-2 text-sm text-gray-700">External API</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="file"
                    checked={formData.data_source.source_type === 'file'}
                    onChange={(e) => setFormData({
                      ...formData,
                      data_source: {
                        source_type: e.target.value as SourceType,
                        location: formData.data_source.location,
                        file_type: 'csv',
                      }
                    })}
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
                  />
                  <span className="ml-2 text-sm text-gray-700">Internal File</span>
                </label>
              </div>
            </div>

            <div>
              <label htmlFor="location" className="block text-sm font-medium text-gray-700">
                {formData.data_source.source_type === 'api' ? 'API URL' : 'File Path'} *
              </label>
              <input
                type="text"
                id="location"
                required
                value={formData.data_source.location}
                onChange={(e) => setFormData({
                  ...formData,
                  data_source: { ...formData.data_source, location: e.target.value }
                })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
                placeholder={formData.data_source.source_type === 'api' ? 'https://api.example.com/data' : './data/input.csv'}
              />
            </div>

            {formData.data_source.source_type === 'file' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  File Type *
                </label>
                <div className="flex space-x-4">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="csv"
                      checked={formData.data_source.file_type === 'csv'}
                      onChange={(e) => setFormData({
                        ...formData,
                        data_source: { ...formData.data_source, file_type: e.target.value as FileType }
                      })}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
                    />
                    <span className="ml-2 text-sm text-gray-700">CSV</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="json"
                      checked={formData.data_source.file_type === 'json'}
                      onChange={(e) => setFormData({
                        ...formData,
                        data_source: { ...formData.data_source, file_type: e.target.value as FileType }
                      })}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
                    />
                    <span className="ml-2 text-sm text-gray-700">JSON</span>
                  </label>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Processing Script</h2>
          
          <div>
            <label htmlFor="processing_script" className="block text-sm font-medium text-gray-700">
              Python Script *
            </label>
            <p className="mt-1 text-xs text-gray-500">
              Your script must accept a DataFrame named 'data' and return a DataFrame named 'result'
            </p>
            <textarea
              id="processing_script"
              required
              rows={10}
              value={formData.processing_script}
              onChange={(e) => setFormData({ ...formData, processing_script: e.target.value })}
              className="mt-2 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border font-mono text-xs"
              placeholder={scriptExample}
            />
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Email Recipients</h2>
          
          <div className="space-y-3">
            {formData.consumer_emails.map((email, index) => (
              <div key={index} className="flex items-center space-x-2">
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => updateEmail(index, e.target.value)}
                  className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
                  placeholder="user@example.com"
                />
                {formData.consumer_emails.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeEmail(index)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-md"
                  >
                    <X className="h-5 w-5" />
                  </button>
                )}
              </div>
            ))}
            <button
              type="button"
              onClick={addEmail}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Email
            </button>
          </div>
        </div>

        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => navigate('/dashboard')}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating...' : 'Create Job'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default CreateJob
