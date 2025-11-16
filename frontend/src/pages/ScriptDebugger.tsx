import { useState, useEffect } from 'react'
import { Play, Upload, Save, FileText, AlertCircle, CheckCircle, Loader } from 'lucide-react'
import { scriptsApi } from '../services/api'
import { Script, ScriptTestResult } from '../types/script'
import Alert from '../components/Alert'

const ScriptDebugger = () => {
  const [scriptContent, setScriptContent] = useState('')
  const [scriptName, setScriptName] = useState('')
  const [description, setDescription] = useState('')
  const [testFile, setTestFile] = useState<File | null>(null)
  const [testFilePath, setTestFilePath] = useState<string | null>(null)
  const [testing, setTesting] = useState(false)
  const [saving, setSaving] = useState(false)
  const [testResult, setTestResult] = useState<ScriptTestResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [savedScripts, setSavedScripts] = useState<Script[]>([])
  const [loadingScripts, setLoadingScripts] = useState(false)

  const scriptExample = `# Your script receives 'data' as a pandas DataFrame
# Process the data and assign the result to 'result'

# Example: Filter and aggregate
filtered = data[data['amount'] > 100]
result = filtered.groupby('category').agg({
    'amount': 'sum',
    'quantity': 'count'
}).reset_index()

# The 'result' DataFrame will be returned`

  useEffect(() => {
    loadSavedScripts()
  }, [])

  const loadSavedScripts = async () => {
    setLoadingScripts(true)
    try {
      const scripts = await scriptsApi.getAllScripts()
      setSavedScripts(scripts)
    } catch (err: any) {
      console.error('Failed to load scripts:', err)
    } finally {
      setLoadingScripts(false)
    }
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setTestFile(file)
      setError(null)
      
      // Upload file immediately
      try {
        const uploadResult = await scriptsApi.uploadTestFile(file)
        setTestFilePath(uploadResult.path)
        setSuccess(`Test file uploaded: ${file.name}`)
        setTimeout(() => setSuccess(null), 3000)
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to upload test file')
        setTestFile(null)
        setTestFilePath(null)
      }
    }
  }

  const handleTest = async () => {
    if (!scriptContent.trim()) {
      setError('Please enter a script to test')
      return
    }

    if (!testFilePath) {
      setError('Please upload a test file first')
      return
    }

    setTesting(true)
    setError(null)
    setTestResult(null)

    try {
      const result = await scriptsApi.testScript({
        script_content: scriptContent,
        test_file_path: testFilePath,
      })
      setTestResult(result)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to test script')
    } finally {
      setTesting(false)
    }
  }

  const handleSave = async () => {
    if (!scriptName.trim()) {
      setError('Please enter a script name')
      return
    }

    if (!scriptContent.trim()) {
      setError('Please enter script content')
      return
    }

    setSaving(true)
    setError(null)

    try {
      await scriptsApi.createScript({
        script_name: scriptName,
        description: description || undefined,
        script_content: scriptContent,
      })
      setSuccess(`Script "${scriptName}" saved successfully!`)
      setTimeout(() => setSuccess(null), 3000)
      
      // Reload scripts list
      await loadSavedScripts()
      
      // Clear form
      setScriptName('')
      setDescription('')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save script')
    } finally {
      setSaving(false)
    }
  }

  const loadScript = (script: Script) => {
    setScriptContent(script.script_content)
    setScriptName(script.script_name)
    setDescription(script.description || '')
    setTestResult(null)
    setSuccess(`Loaded script: ${script.script_name}`)
    setTimeout(() => setSuccess(null), 3000)
  }

  return (
    <div className="px-4 sm:px-0">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Script Debugger</h1>
        <p className="mt-2 text-sm text-gray-700">
          Write, test, and debug your data processing scripts with live feedback
        </p>
      </div>

      {error && (
        <div className="mb-6">
          <Alert type="error" title="Error" message={error} onClose={() => setError(null)} />
        </div>
      )}

      {success && (
        <div className="mb-6">
          <Alert type="success" title="Success" message={success} onClose={() => setSuccess(null)} />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Script Editor */}
        <div className="lg:col-span-2 space-y-6">
          {/* Test File Upload */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Test Data</h2>
            <div>
              <label htmlFor="test-file-upload" className="block text-sm font-medium text-gray-700 mb-2">
                Upload Test File (CSV or JSON)
              </label>
              <div className="flex items-center space-x-4">
                <label
                  htmlFor="test-file-upload"
                  className="flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 cursor-pointer"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Choose File
                </label>
                <input
                  id="test-file-upload"
                  type="file"
                  accept=".csv,.json"
                  onChange={handleFileChange}
                  className="hidden"
                />
                {testFile && (
                  <span className="text-sm text-gray-600">
                    {testFile.name} ({(testFile.size / 1024).toFixed(2)} KB)
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Script Editor */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Python Script</h2>
              <button
                onClick={handleTest}
                disabled={testing || !testFilePath}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {testing ? (
                  <>
                    <Loader className="h-4 w-4 mr-2 animate-spin" />
                    Testing...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Run Test
                  </>
                )}
              </button>
            </div>
            
            <textarea
              value={scriptContent}
              onChange={(e) => setScriptContent(e.target.value)}
              className="w-full h-96 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 font-mono text-sm px-3 py-2 border"
              placeholder={scriptExample}
            />
            
            <div className="mt-4 text-xs text-gray-500 bg-gray-50 p-3 rounded">
              <p className="font-medium mb-1">Tips:</p>
              <ul className="list-disc list-inside space-y-1">
                <li>Input data is available as <code className="bg-gray-200 px-1 rounded">data</code> (pandas DataFrame)</li>
                <li>Assign your output to <code className="bg-gray-200 px-1 rounded">result</code></li>
                <li>Available libraries: pandas (pd), numpy (np), datetime</li>
              </ul>
            </div>
          </div>

          {/* Test Results */}
          {testResult && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Test Results</h2>
              
              {testResult.success ? (
                <div className="space-y-4">
                  <div className="flex items-center text-green-600">
                    <CheckCircle className="h-5 w-5 mr-2" />
                    <span className="font-medium">Script executed successfully!</span>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Input Shape:</p>
                      <p className="font-mono">{testResult.input_shape?.join(' × ')}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Output Shape:</p>
                      <p className="font-mono">{testResult.output_shape?.join(' × ')}</p>
                    </div>
                  </div>

                  <div>
                    <p className="text-sm text-gray-500 mb-2">Output Columns:</p>
                    <div className="flex flex-wrap gap-2">
                      {testResult.output_columns?.map((col) => (
                        <span key={col} className="px-2 py-1 bg-indigo-100 text-indigo-800 text-xs rounded">
                          {col} ({testResult.output_dtypes?.[col]})
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <p className="text-sm text-gray-500 mb-2">Output Preview (first 10 rows):</p>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200 text-xs">
                        <thead className="bg-gray-50">
                          <tr>
                            {testResult.output_columns?.map((col) => (
                              <th key={col} className="px-3 py-2 text-left font-medium text-gray-500 uppercase tracking-wider">
                                {col}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {testResult.output_preview?.map((row, idx) => (
                            <tr key={idx}>
                              {testResult.output_columns?.map((col) => (
                                <td key={col} className="px-3 py-2 whitespace-nowrap">
                                  {String(row[col])}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center text-red-600">
                    <AlertCircle className="h-5 w-5 mr-2" />
                    <span className="font-medium">Script execution failed</span>
                  </div>
                  
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-1">Error Type:</p>
                    <p className="text-sm text-red-600 font-mono">{testResult.error_type}</p>
                  </div>

                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-1">Error Message:</p>
                    <p className="text-sm text-red-600">{testResult.error}</p>
                  </div>

                  {testResult.traceback && (
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-1">Traceback:</p>
                      <pre className="text-xs bg-gray-900 text-gray-100 p-3 rounded overflow-x-auto">
                        {testResult.traceback}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Save Script */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Save Script</h2>
            
            <div className="space-y-4">
              <div>
                <label htmlFor="script_name" className="block text-sm font-medium text-gray-700">
                  Script Name *
                </label>
                <input
                  type="text"
                  id="script_name"
                  value={scriptName}
                  onChange={(e) => setScriptName(e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
                  placeholder="my_data_processor"
                />
              </div>

              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                  Description (optional)
                </label>
                <input
                  type="text"
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
                  placeholder="Filters and aggregates sales data"
                />
              </div>

              <button
                onClick={handleSave}
                disabled={saving}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {saving ? (
                  <>
                    <Loader className="h-4 w-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Save Script
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Right Column - Saved Scripts */}
        <div className="lg:col-span-1">
          <div className="bg-white shadow rounded-lg p-6 sticky top-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Saved Scripts</h2>
            
            {loadingScripts ? (
              <div className="flex justify-center py-8">
                <Loader className="h-6 w-6 animate-spin text-indigo-600" />
              </div>
            ) : savedScripts.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-8">No saved scripts yet</p>
            ) : (
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {savedScripts.map((script) => (
                  <button
                    key={script.script_name}
                    onClick={() => loadScript(script)}
                    className="w-full text-left p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start">
                      <FileText className="h-4 w-4 text-indigo-600 mt-0.5 mr-2 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {script.script_name}
                        </p>
                        {script.description && (
                          <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                            {script.description}
                          </p>
                        )}
                        <p className="text-xs text-gray-400 mt-1">
                          Updated: {new Date(script.updated_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ScriptDebugger
