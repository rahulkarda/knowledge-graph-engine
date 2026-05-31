import { Routes, Route, Navigate } from 'react-router-dom'
import AppShell from './components/layout/AppShell'
import Dashboard from './pages/Dashboard'
import GraphView from './pages/GraphView'
import Capture from './pages/Capture'
import Search from './pages/Search'
import NodeDetail from './pages/NodeDetail'
import Connections from './pages/Connections'
import QAPage from './pages/QAPage'
import Timeline from './pages/Timeline'
import Tags from './pages/Tags'

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/graph" element={<GraphView />} />
        <Route path="/capture" element={<Capture />} />
        <Route path="/search" element={<Search />} />
        <Route path="/nodes/:id" element={<NodeDetail />} />
        <Route path="/connections" element={<Connections />} />
        <Route path="/qa" element={<QAPage />} />
        <Route path="/timeline" element={<Timeline />} />
        <Route path="/tags" element={<Tags />} />
      </Routes>
    </AppShell>
  )
}
