import { Navigate } from 'react-router-dom'
import { useAuth } from '../lib/auth'

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth()

  if (isLoading) return <div className="p-8 text-center font-tajawal">جاري التحميل...</div>
  if (!user) return <Navigate to="/login" replace />

  return <>{children}</>
}
