export type SourceType = 'api' | 'file'
export type FileType = 'csv' | 'json'

export interface DataSource {
  source_type: SourceType
  location: string
  file_type?: FileType
}

export interface JobCreate {
  job_name: string
  schedule_time: string
  data_source: DataSource
  processing_script: string
  consumer_emails: string[]
}

export interface Job {
  job_name: string
  schedule_time: string
  data_source: DataSource
  processing_script: string
  consumer_emails: string[]
  created_at: string
  last_run?: string
}
