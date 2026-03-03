import { Link } from 'react-router-dom'
import type { TrainingSession, SamplingStrategy } from '../lib/types'
import { STRATEGY_LABELS } from '../lib/types'

interface SessionHistoryListProps {
  sessions: TrainingSession[]
}

function toArabicDigits(n: number): string {
  const arabicDigits = ['\u0660', '\u0661', '\u0662', '\u0663', '\u0664', '\u0665', '\u0666', '\u0667', '\u0668', '\u0669']
  return String(n)
    .split('')
    .map((d) => arabicDigits[Number(d)] ?? d)
    .join('')
}

export default function SessionHistoryList({ sessions }: SessionHistoryListProps) {
  if (sessions.length === 0) return null

  return (
    <div className="space-y-3">
      {sessions.map((session) => {
        const isCompleted = session.status === 'completed'
        const correctCount = session.correct_count ?? 0
        const total = session.total_items
        const percentage = total > 0 ? Math.round((correctCount / total) * 100) : 0
        const dateStr = new Date(session.created_at).toLocaleDateString('ar-SA', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
        })

        return (
          <div
            key={session.id}
            className="flex items-center justify-between rounded-xl bg-white px-5 py-4 shadow-sm"
          >
            <div className="flex flex-col gap-1">
              <span className="text-sm text-gray-500">{dateStr}</span>
              <div className="flex items-center gap-2">
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                    isCompleted
                      ? 'bg-green-100 text-green-700'
                      : 'bg-amber-100 text-amber-700'
                  }`}
                >
                  {isCompleted ? '\u0645\u0643\u062a\u0645\u0644\u0629' : '\u0642\u064a\u062f \u0627\u0644\u062a\u0642\u062f\u0645'}
                </span>
                {session.strategy && session.strategy !== 'sequential' && (
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                      session.strategy === 'uncertainty'
                        ? 'bg-amber-100 text-amber-700'
                        : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {STRATEGY_LABELS[session.strategy as SamplingStrategy]}
                  </span>
                )}
                <span className="text-sm text-gray-600">
                  {isCompleted
                    ? `${toArabicDigits(correctCount)}/${toArabicDigits(total)} (${toArabicDigits(percentage)}%)`
                    : '\u2014'}
                </span>
              </div>
            </div>

            <Link
              to={
                isCompleted
                  ? `/train/sessions/${session.id}/summary`
                  : `/train/sessions/${session.id}`
              }
              className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-semibold text-mizan-navy transition-colors hover:bg-gray-200"
            >
              {isCompleted ? '\u0645\u0631\u0627\u062c\u0639\u0629' : '\u0627\u0633\u062a\u0645\u0631\u0627\u0631'}
            </Link>
          </div>
        )
      })}
    </div>
  )
}
