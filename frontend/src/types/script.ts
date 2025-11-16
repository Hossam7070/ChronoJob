export interface ScriptCreate {
  script_name: string
  description?: string
  script_content: string
}

export interface Script {
  script_name: string
  description?: string
  script_content: string
  created_at: string
  updated_at: string
}

export interface ScriptTestRequest {
  script_content: string
  test_file_path: string
}

export interface ScriptTestResult {
  success: boolean
  input_shape: number[] | null
  output_shape: number[] | null
  input_columns: string[] | null
  output_columns: string[] | null
  output_preview: any[] | null
  output_dtypes: Record<string, string> | null
  error: string | null
  error_type: string | null
  traceback: string | null
}
