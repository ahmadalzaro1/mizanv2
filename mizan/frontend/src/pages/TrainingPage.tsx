import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { createSession, listSessions, getStrategyAvailability } from '../lib/training-api'
import type { StrategyAvailability } from '../lib/training-api'
import type { TrainingSession, SamplingStrategy } from '../lib/types'
import { STRATEGY_LABELS } from '../lib/types'
import SessionHistoryList from '../components/SessionHistoryList'

interface StrategyConfig {
  id: SamplingStrategy
  name: string
  desc: string
  disabledMsg: string
  accentBorder: string
  accentBg: string
  accentRing: string
  accentText: string
}

const STRATEGIES: StrategyConfig[] = [
  {
    id: 'sequential',
    name: STRATEGY_LABELS.sequential,
    desc: 'أمثلة عشوائية للتعلم الأساسي',
    disabledMsg: '',
    accentBorder: 'border-green-500',
    accentBg: 'bg-green-50',
    accentRing: 'ring-green-500',
    accentText: 'text-green-700',
  },
  {
    id: 'uncertainty',
    name: STRATEGY_LABELS.uncertainty,
    desc: 'أمثلة يصعب على الذكاء الاصطناعي تصنيفها',
    disabledMsg: 'يتطلب تحميل النموذج',
    accentBorder: 'border-amber-500',
    accentBg: 'bg-amber-50',
    accentRing: 'ring-amber-500',
    accentText: 'text-amber-700',
  },
  {
    id: 'disagreement',
    name: STRATEGY_LABELS.disagreement,
    desc: 'أمثلة اختلف عليها المشرفون الآخرون',
    disabledMsg: 'يتطلب جلسة سابقة واحدة على الأقل',
    accentBorder: 'border-red-500',
    accentBg: 'bg-red-50',
    accentRing: 'ring-red-500',
    accentText: 'text-red-700',
  },
]

export default function TrainingPage() {
  const navigate = useNavigate()
  const [sessions, setSessions] = useState<TrainingSession[]>([])
  const [availability, setAvailability] = useState<StrategyAvailability>({
    sequential: true,
    uncertainty: false,
    disagreement: false,
  })
  const [selectedStrategy, setSelectedStrategy] = useState<SamplingStrategy>('sequential')
  const [isLoading, setIsLoading] = useState(true)
  const [isCreating, setIsCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([listSessions(), getStrategyAvailability()])
      .then(([sessionData, availData]) => {
        setSessions(sessionData)
        setAvailability(availData)
      })
      .catch(() => {
        setError('حدث خطأ في تحميل الجلسات')
      })
      .finally(() => {
        setIsLoading(false)
      })
  }, [])

  function handleStartTraining() {
    setIsCreating(true)
    setError(null)
    createSession(selectedStrategy)
      .then((session) => {
        navigate(`/train/sessions/${session.id}`)
      })
      .catch((err: unknown) => {
        const axiosErr = err as { response?: { data?: { detail?: string } } }
        setError(axiosErr.response?.data?.detail || 'حدث خطأ')
      })
      .finally(() => {
        setIsCreating(false)
      })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <p className="font-tajawal text-lg text-gray-500">جارٍ التحميل...</p>
      </div>
    )
  }

  const strategyPicker = (
    <div className="mb-6">
      <h3 className="mb-3 text-base font-bold text-mizan-navy">اختر أسلوب التدريب</h3>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        {STRATEGIES.map((s) => {
          const isDisabled = !availability[s.id]
          const isSelected = selectedStrategy === s.id
          return (
            <button
              key={s.id}
              type="button"
              onClick={() => !isDisabled && setSelectedStrategy(s.id)}
              disabled={isDisabled}
              className={[
                'rounded-xl border-t-4 p-4 text-start shadow-sm transition-all',
                s.accentBorder,
                isDisabled
                  ? 'bg-gray-50 opacity-50 cursor-not-allowed'
                  : `${s.accentBg} cursor-pointer hover:shadow-md`,
                isSelected && !isDisabled ? `ring-2 ring-offset-2 ${s.accentRing}` : '',
              ].join(' ')}
            >
              <p className={`font-tajawal text-sm font-bold ${isDisabled ? 'text-gray-500' : s.accentText}`}>
                {s.name}
              </p>
              <p className="mt-1 font-tajawal text-xs text-gray-600">{s.desc}</p>
              {isDisabled && s.disabledMsg && (
                <p className="mt-2 font-tajawal text-xs text-gray-400">{s.disabledMsg}</p>
              )}
            </button>
          )
        })}
      </div>
    </div>
  )

  return (
    <div dir="rtl" className="font-tajawal">
      {sessions.length === 0 ? (
        <div className="mx-auto max-w-2xl py-12">
          <div className="mb-6 text-center">
            <h2 className="mb-4 text-2xl font-bold text-mizan-navy">مرحباً بك في التدريب</h2>
            <p className="mb-6 text-gray-600">
              ستعرض عليك ٢٠ تغريدة عربية. صنِّف كل واحدة: خطاب كراهية أو ليس كراهية.
            </p>
          </div>
          {strategyPicker}
          <div className="text-center">
            <button
              type="button"
              disabled={isCreating}
              onClick={handleStartTraining}
              className="rounded-lg bg-mizan-navy px-8 py-4 text-lg font-bold text-white transition-colors hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isCreating ? 'جارٍ الإنشاء...' : 'ابدأ التدريب'}
            </button>
          </div>
        </div>
      ) : (
        <div>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-bold text-mizan-navy">جلسات التدريب</h2>
            <button
              type="button"
              disabled={isCreating}
              onClick={handleStartTraining}
              className="rounded-lg bg-mizan-navy px-6 py-2 text-sm font-bold text-white transition-colors hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isCreating ? 'جارٍ الإنشاء...' : 'ابدأ جلسة جديدة'}
            </button>
          </div>
          {strategyPicker}
          <SessionHistoryList sessions={sessions} />
        </div>
      )}

      {error && (
        <div className="mt-4 rounded-lg bg-red-50 p-3 text-center text-sm text-red-700">
          {error}
        </div>
      )}
    </div>
  )
}
