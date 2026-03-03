import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { getSession, createSession } from '../lib/training-api'
import type { TrainingSession } from '../lib/types'
import { toArabicDigits } from '../lib/format'

export default function SessionSummary() {
  const { sessionId } = useParams()
  const navigate = useNavigate()

  const [session, setSession] = useState<TrainingSession | null>(null)
  const [isCreating, setIsCreating] = useState(false)

  useEffect(() => {
    getSession(sessionId!)
      .then((data) => {
        if (data.status !== 'completed') {
          navigate(`/train/sessions/${data.id}`, { replace: true })
          return
        }
        setSession(data)
      })
      .catch(() => {
        navigate('/train', { replace: true })
      })
  }, [sessionId, navigate])

  function handleNewSession() {
    setIsCreating(true)
    createSession('sequential')
      .then((newSession) => {
        navigate(`/train/sessions/${newSession.id}`)
      })
      .catch(() => {
        navigate('/train')
      })
      .finally(() => {
        setIsCreating(false)
      })
  }

  if (!session) {
    return (
      <div className="flex items-center justify-center py-20">
        <p className="font-tajawal text-lg text-gray-500">
          {'\u062c\u0627\u0631\u064d \u0627\u0644\u062a\u062d\u0645\u064a\u0644...'}
        </p>
      </div>
    )
  }

  const correctCount = session.correct_count ?? 0
  const totalItems = session.total_items
  const percentage = totalItems > 0 ? Math.round((correctCount / totalItems) * 100) : 0
  const items = session.items ?? []

  let scoreColorClass: string
  let scoreMessage: string
  if (percentage >= 80) {
    scoreColorClass = 'bg-green-100 text-green-800'
    scoreMessage = '\u0645\u0645\u062a\u0627\u0632!'
  } else if (percentage >= 60) {
    scoreColorClass = 'bg-amber-100 text-amber-800'
    scoreMessage = '\u062c\u064a\u062f'
  } else {
    scoreColorClass = 'bg-red-100 text-red-800'
    scoreMessage = '\u064a\u062d\u062a\u0627\u062c \u062a\u062d\u0633\u064a\u0646'
  }

  return (
    <div dir="rtl" className="font-tajawal">
      {/* Score card */}
      <div className={`mb-6 rounded-xl p-8 text-center ${scoreColorClass}`}>
        <p className="mb-2 text-lg font-semibold">{scoreMessage}</p>
        <p className="text-4xl font-bold">
          {toArabicDigits(correctCount)} {'\u0645\u0646'} {toArabicDigits(totalItems)}
        </p>
        <p className="mt-1 text-lg">
          ({toArabicDigits(percentage)}%)
        </p>
      </div>

      {/* Item breakdown */}
      {items.length > 0 && (
        <div className="mb-6">
          <h3 className="mb-3 text-lg font-bold text-mizan-navy">
            {'\u062a\u0641\u0627\u0635\u064a\u0644 \u0627\u0644\u0625\u062c\u0627\u0628\u0627\u062a'}
          </h3>
          <div className="max-h-80 overflow-y-auto rounded-xl bg-white shadow-sm">
            {items.map((item, idx) => (
              <div
                key={item.id}
                className={`flex items-center gap-3 px-4 py-3 ${
                  idx < items.length - 1 ? 'border-b border-gray-100' : ''
                }`}
              >
                <span className="flex-shrink-0 text-lg">
                  {item.is_correct ? (
                    <span className="text-green-600">&#10003;</span>
                  ) : (
                    <span className="text-red-600">&#10007;</span>
                  )}
                </span>
                <p className="line-clamp-1 flex-1 text-sm text-gray-700">
                  {item.content_example.text.length > 60
                    ? item.content_example.text.slice(0, 60) + '...'
                    : item.content_example.text}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-col gap-3">
        <button
          type="button"
          disabled={isCreating}
          onClick={handleNewSession}
          className="w-full rounded-lg bg-mizan-navy px-4 py-3 text-lg font-bold text-white transition-colors hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isCreating
            ? '\u062c\u0627\u0631\u064d \u0627\u0644\u0625\u0646\u0634\u0627\u0621...'
            : '\u0627\u0628\u062f\u0623 \u062c\u0644\u0633\u0629 \u062c\u062f\u064a\u062f\u0629'}
        </button>
        <Link
          to="/"
          className="block w-full rounded-lg border-2 border-gray-300 bg-white px-4 py-3 text-center text-lg font-bold text-gray-700 transition-colors hover:bg-gray-50"
        >
          {'\u0627\u0644\u0639\u0648\u062f\u0629 \u0625\u0644\u0649 \u0644\u0648\u062d\u0629 \u0627\u0644\u062a\u062d\u0643\u0645'}
        </Link>
      </div>
    </div>
  )
}
