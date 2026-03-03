import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './lib/auth'
import { TourProvider } from './components/OnboardingTour'
import { ProtectedRoute } from './components/ProtectedRoute'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import CreateModerator from './pages/admin/CreateModerator'
import TrainingPage from './pages/TrainingPage'
import TrainingSessionPage from './pages/TrainingSession'
import SessionSummary from './pages/SessionSummary'
import ObservatoryPage from './pages/ObservatoryPage'
import BiasAuditorPage from './pages/BiasAuditorPage'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <TourProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<ProtectedRoute><Layout><Dashboard /></Layout></ProtectedRoute>} />
            <Route path="/admin/moderators/new" element={<ProtectedRoute><Layout><CreateModerator /></Layout></ProtectedRoute>} />
            <Route path="/observatory" element={<ProtectedRoute><Layout><ObservatoryPage /></Layout></ProtectedRoute>} />
            <Route path="/audit" element={<ProtectedRoute><Layout><BiasAuditorPage /></Layout></ProtectedRoute>} />
            <Route path="/train" element={<ProtectedRoute><Layout><TrainingPage /></Layout></ProtectedRoute>} />
            <Route path="/train/sessions/:sessionId" element={<ProtectedRoute><Layout><TrainingSessionPage /></Layout></ProtectedRoute>} />
            <Route path="/train/sessions/:sessionId/summary" element={<ProtectedRoute><Layout><SessionSummary /></Layout></ProtectedRoute>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </TourProvider>
      </BrowserRouter>
    </AuthProvider>
  )
}
