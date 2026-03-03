import { useAuth } from '../lib/auth'
import { useLocation, Link } from 'react-router-dom'
import { useTour } from './OnboardingTour'

const navItems = [
  { to: '/observatory', label: 'المرصد' },
  { to: '/audit', label: 'مدقق التحيز' },
  { to: '/train', label: 'التدريب' },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth()
  const { pathname } = useLocation()
  const { startTour, tourSeen } = useTour()

  return (
    <div className="min-h-screen bg-mizan-surface font-tajawal">
      {/* Header */}
      <header className="bg-mizan-navy text-white px-8 py-4 flex items-center justify-between">
        <Link to="/" id="tour-logo" className="text-2xl font-bold text-white no-underline">
          ميزان
        </Link>
        <div className="flex items-center gap-4">
          <span className="text-sm opacity-85">{user?.full_name}</span>
          <button
            onClick={startTour}
            title="جولة تعريفية"
            aria-label="جولة تعريفية"
            className={`w-8 h-8 rounded-full border border-white/60 text-white text-sm font-bold flex items-center justify-center hover:border-white transition-colors ${!tourSeen ? 'animate-pulse' : ''}`}
          >
            ?
          </button>
          <button
            onClick={logout}
            className="px-4 py-1.5 bg-transparent text-white border border-white/40 rounded text-sm font-tajawal cursor-pointer hover:border-white/70 transition-colors"
          >
            خروج
          </button>
        </div>
      </header>

      {/* Navigation */}
      <nav id="tour-nav" className="bg-white border-b border-gray-200 px-8 flex gap-2">
        {navItems.map(({ to, label }) => (
          <Link
            key={to}
            to={to}
            className={`block px-5 py-4 text-mizan-navy no-underline font-medium border-b-3 transition-colors ${
              pathname.startsWith(to)
                ? 'border-mizan-navy'
                : 'border-transparent hover:border-gray-300'
            }`}
          >
            {label}
          </Link>
        ))}
        {(user?.role === 'admin' || user?.role === 'super_admin') && (
          <Link
            to="/admin/moderators/new"
            className={`block px-5 py-4 text-gray-500 no-underline text-sm border-b-3 transition-colors ${
              pathname.startsWith('/admin')
                ? 'border-mizan-navy text-mizan-navy'
                : 'border-transparent hover:border-gray-300'
            }`}
          >
            إدارة المستخدمين
          </Link>
        )}
      </nav>

      {/* Main content */}
      <main className="max-w-5xl mx-auto px-8 py-8">
        {children}
      </main>
    </div>
  )
}
