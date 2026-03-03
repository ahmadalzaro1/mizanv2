import { useState } from 'react'
import { useAuth } from '../../lib/auth'
import { api } from '../../lib/api'

export default function CreateModerator() {
  const { user } = useAuth()
  const [form, setForm] = useState({ email: '', full_name: '', password: '', role: 'moderator' })
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)
    try {
      const res = await api.post('/auth/users', form)
      setSuccess(`تم إنشاء الحساب بنجاح: ${res.data.email}`)
      setForm({ email: '', full_name: '', password: '', role: 'moderator' })
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(detail ?? 'حدث خطأ أثناء إنشاء الحساب')
    } finally {
      setLoading(false)
    }
  }

  // Role guard — only admins should reach this page
  if (!user || (user.role !== 'admin' && user.role !== 'super_admin')) {
    return (
      <div dir="rtl" style={{ fontFamily: 'Tajawal, sans-serif', padding: '2rem', color: '#c0392b' }}>
        غير مصرح لك بالوصول إلى هذه الصفحة.
      </div>
    )
  }

  return (
    <div dir="rtl" style={{ fontFamily: "'Tajawal', sans-serif", minHeight: '100vh', backgroundColor: '#f9f9f9' }}>
      {/* Header */}
      <header style={{
        backgroundColor: '#1a1a2e',
        color: 'white',
        padding: '1rem 2rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <a href="/" style={{ color: 'white', textDecoration: 'none', fontSize: '1.3rem', fontWeight: 700 }}>ميزان</a>
        <span style={{ fontSize: '0.9rem', opacity: 0.85 }}>{user.full_name}</span>
      </header>

      <main style={{ padding: '2rem', maxWidth: '520px', margin: '0 auto' }}>
        <h2 style={{ color: '#1a1a2e', marginBottom: '1.5rem' }}>إضافة مستخدم جديد</h2>

        <div style={{ background: 'white', borderRadius: '8px', padding: '1.5rem', border: '1px solid #eee' }}>
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.4rem', fontWeight: '500' }}>الاسم الكامل</label>
              <input
                type="text"
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                required
                style={{ width: '100%', padding: '0.6rem 0.75rem', borderRadius: '6px', border: '1px solid #ddd', fontSize: '1rem', boxSizing: 'border-box', textAlign: 'right' }}
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.4rem', fontWeight: '500' }}>البريد الإلكتروني</label>
              <input
                type="text"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                required
                dir="ltr"
                style={{ width: '100%', padding: '0.6rem 0.75rem', borderRadius: '6px', border: '1px solid #ddd', fontSize: '1rem', boxSizing: 'border-box' }}
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.4rem', fontWeight: '500' }}>كلمة المرور</label>
              <input
                type="password"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                required
                dir="ltr"
                style={{ width: '100%', padding: '0.6rem 0.75rem', borderRadius: '6px', border: '1px solid #ddd', fontSize: '1rem', boxSizing: 'border-box' }}
              />
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', marginBottom: '0.4rem', fontWeight: '500' }}>الدور</label>
              <select
                value={form.role}
                onChange={(e) => setForm({ ...form, role: e.target.value })}
                style={{ width: '100%', padding: '0.6rem 0.75rem', borderRadius: '6px', border: '1px solid #ddd', fontSize: '1rem', fontFamily: 'Tajawal, sans-serif' }}
              >
                <option value="moderator">مشرف</option>
                <option value="admin">مدير</option>
              </select>
            </div>

            {success && (
              <p style={{ color: '#27ae60', marginBottom: '1rem', padding: '0.75rem', backgroundColor: '#eafaf1', borderRadius: '4px', fontSize: '0.9rem' }}>
                {success}
              </p>
            )}
            {error && (
              <p style={{ color: '#c0392b', marginBottom: '1rem', padding: '0.75rem', backgroundColor: '#fdedec', borderRadius: '4px', fontSize: '0.9rem' }}>
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              style={{
                width: '100%',
                padding: '0.75rem',
                backgroundColor: '#1a1a2e',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '1rem',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontFamily: "'Tajawal', sans-serif",
                opacity: loading ? 0.7 : 1,
              }}
            >
              {loading ? 'جاري الإنشاء...' : 'إنشاء الحساب'}
            </button>
          </form>
        </div>

        <p style={{ marginTop: '1rem', fontSize: '0.85rem', color: '#888' }}>
          <a href="/" style={{ color: '#1a1a2e' }}>← العودة إلى الرئيسية</a>
        </p>
      </main>
    </div>
  )
}
