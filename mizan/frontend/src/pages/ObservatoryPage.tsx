import { useState, useEffect } from 'react'
import { getTrends } from '../lib/observatory-api'
import type { MonthlyData, HistoricalEvent } from '../lib/observatory-api'
import TimelineChart from '../components/TimelineChart'
import { toArabicDigits } from '../lib/format'

export default function ObservatoryPage() {
  const [monthly, setMonthly] = useState<MonthlyData[]>([])
  const [events, setEvents] = useState<HistoricalEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getTrends()
      .then((data) => {
        setMonthly(data.monthly)
        setEvents(data.events)
      })
      .catch(() => setError('حدث خطأ أثناء تحميل البيانات'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <p className="font-tajawal text-lg text-gray-500">جارٍ التحميل...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg bg-red-50 p-6 text-center">
        <p className="font-tajawal text-red-700">{error}</p>
      </div>
    )
  }

  // Summary stats
  const totalHate = monthly.reduce((sum, d) => sum + d.hate_count, 0)
  const totalTweets = monthly.reduce((sum, d) => sum + d.total_count, 0)
  const hatePercent = totalTweets > 0 ? Math.round((totalHate / totalTweets) * 100) : 0
  const yearRange = monthly.length > 0
    ? `${monthly[0].year}–${monthly[monthly.length - 1].year}`
    : ''

  return (
    <div dir="rtl" className="font-tajawal">
      {/* Header */}
      <h2 className="mb-2 text-2xl font-bold text-mizan-navy">
        المرصد — اتجاهات خطاب الكراهية في الأردن
      </h2>
      <p className="mb-6 text-gray-500">
        تحليل بيانات مجموعة JHSC على مدى ٨ سنوات ({yearRange})
      </p>

      {/* Summary cards */}
      <div className="mb-6 grid grid-cols-3 gap-4">
        <div className="rounded-lg bg-white p-4 text-center shadow-sm">
          <p className="text-3xl font-bold text-mizan-navy">{toArabicDigits(totalTweets)}</p>
          <p className="text-sm text-gray-500">إجمالي التغريدات</p>
        </div>
        <div className="rounded-lg bg-red-50 p-4 text-center shadow-sm">
          <p className="text-3xl font-bold text-red-700">{toArabicDigits(totalHate)}</p>
          <p className="text-sm text-gray-500">تغريدات خطاب كراهية</p>
        </div>
        <div className="rounded-lg bg-amber-50 p-4 text-center shadow-sm">
          <p className="text-3xl font-bold text-amber-700">{toArabicDigits(hatePercent)}٪</p>
          <p className="text-sm text-gray-500">نسبة خطاب الكراهية</p>
        </div>
      </div>

      {/* Timeline chart */}
      <div className="rounded-xl bg-white p-6 shadow-sm">
        <h3 className="mb-4 text-lg font-bold text-mizan-navy">
          حجم خطاب الكراهية الشهري
        </h3>
        <TimelineChart data={monthly} events={events} />
      </div>

      {/* Events legend */}
      <div className="mt-6 rounded-xl bg-white p-6 shadow-sm">
        <h3 className="mb-3 text-lg font-bold text-mizan-navy">
          الأحداث التاريخية المرجعية
        </h3>
        <div className="grid grid-cols-2 gap-3">
          {events.map((event) => (
            <div key={`${event.year}-${event.month}`} className="flex items-start gap-2 text-sm">
              <span className="mt-0.5 flex-shrink-0 text-gray-400">
                {toArabicDigits(event.year)}/{toArabicDigits(event.month)}
              </span>
              <span className="text-gray-700">{event.label_ar}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
