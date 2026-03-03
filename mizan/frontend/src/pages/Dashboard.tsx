import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../lib/auth'
import { useTour, isTourSeen } from '../components/OnboardingTour'

const cards = [
  {
    to: '/observatory',
    id: 'tour-card-observatory',
    title: 'المرصد',
    persona: 'رانيا — مسؤولة سياسات',
    desc: 'تحليل اتجاهات خطاب الكراهية في الأردن على مدى ٨ سنوات',
    accent: 'border-red-500',
    bg: 'bg-red-50',
  },
  {
    to: '/audit',
    id: 'tour-card-audit',
    title: 'مدقق التحيز',
    persona: 'لينا — باحثة NLP',
    desc: 'تقييم عدالة نموذج MARBERT حسب فئات خطاب الكراهية',
    accent: 'border-blue-500',
    bg: 'bg-blue-50',
  },
  {
    to: '/train',
    id: 'tour-card-training',
    title: 'التدريب',
    persona: 'خالد — مشرف محتوى',
    desc: 'تدريب المشرفين على تصنيف المحتوى العربي بمساعدة الذكاء الاصطناعي',
    accent: 'border-green-500',
    bg: 'bg-green-50',
  },
]

export default function Dashboard() {
  const { user } = useAuth()
  const { startTour } = useTour()

  useEffect(() => {
    if (!isTourSeen()) {
      const timer = setTimeout(() => startTour(), 500)
      return () => clearTimeout(timer)
    }
  }, [startTour])

  return (
    <div dir="rtl" className="font-tajawal">
      <h2 className="mb-1 text-2xl font-bold text-mizan-navy">
        مرحباً، {user?.full_name}
      </h2>
      <p className="mb-8 text-gray-500">
        اختر أحد الأقسام الثلاثة للبدء
      </p>

      <div className="grid grid-cols-3 gap-6">
        {cards.map(({ to, id, title, persona, desc, accent, bg }) => (
          <Link
            key={to}
            to={to}
            id={id}
            className={`block rounded-xl border-t-4 ${accent} ${bg} p-6 no-underline shadow-sm transition-shadow hover:shadow-md`}
          >
            <h3 className="mb-1 text-lg font-bold text-mizan-navy">{title}</h3>
            <p className="mb-3 text-xs font-medium text-gray-400">{persona}</p>
            <p className="m-0 text-sm leading-relaxed text-gray-600">{desc}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
