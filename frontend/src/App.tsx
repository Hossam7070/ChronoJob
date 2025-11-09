import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import CreateJob from './pages/CreateJob'
import EditJob from './pages/EditJob'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/create" element={<CreateJob />} />
          <Route path="/edit/:jobName" element={<EditJob />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
