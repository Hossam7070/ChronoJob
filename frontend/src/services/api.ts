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

  testJob: async (jobName: string): Promise<Blob> => {
    const response = await api.post(`/jobs/${jobName}/test`, null, {
      responseType: 'blob',
    })
    return response.data
  },

  updateJob: async (jobName: string, job: JobCreate): Promise<Job> => {
    const response = await api.put<Job>(`/jobs/${jobName}`, job)
    return response.data
  },

  uploadFile: async (file: File): Promise<{ filename: string; path: string; size: number }> => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/jobs/upload-file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },
}

export default api
