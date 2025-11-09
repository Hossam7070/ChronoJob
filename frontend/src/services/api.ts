import axios from 'axios'
import { Job, JobCreate } from '../types/job'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const jobsApi = {
  getAllJobs: async (): Promise<Job[]> => {
    const response = await api.get<Job[]>('/jobs')
    return response.data
  },

  getJob: async (jobName: string): Promise<Job> => {
    const response = await api.get<Job>(`/jobs/${jobName}`)
    return response.data
  },

  createJob: async (job: JobCreate): Promise<Job> => {
    const response = await api.post<Job>('/jobs/create', job)
    return response.data
  },

  deleteJob: async (jobName: string): Promise<void> => {
    await api.delete(`/jobs/${jobName}`)
  },
}

export default api
