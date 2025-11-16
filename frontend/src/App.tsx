import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import CreateJob from './pages/CreateJob'
import EditJob from './pages/EditJob'
import ScriptDebugger from './pages/ScriptDebugger'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/create" element={<CreateJob />} />
          <Route path="/edit/:jobName" element={<EditJob />} />
          <Route path="/script-debugger" element={<ScriptDebugger />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
