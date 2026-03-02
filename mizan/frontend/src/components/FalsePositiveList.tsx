import type { FalsePositiveSample } from '../lib/audit-api'
import { toArabicDigits } from '../lib/format'

interface FalsePositiveListProps {
  samples: FalsePositiveSample[]
}

const MAX_DISPLAY = 10
const MAX_TEXT_LEN = 120

function confidenceBarColor(confidence: number): string {
  if (confidence >= 0.8) return 'bg-red-500'
  if (confidence >= 0.6) return 'bg-amber-500'
  return 'bg-blue-500'
}

function truncateText(text: string): string {
  if (text.length <= MAX_TEXT_LEN) return text
  return text.slice(0, MAX_TEXT_LEN) + '...'
}

export default function FalsePositiveList({ samples }: FalsePositiveListProps) {
  if (samples.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <p className="text-green-700 font-tajawal text-sm font-medium">
          لم يتم العثور على إيجابيات كاذبة
        </p>
      </div>
    )
  }

  const displayed = samples.slice(0, MAX_DISPLAY)

  return (
    <div dir="rtl">
      {displayed.map((sample, idx) => {
        const confidencePct = Math.round(sample.confidence * 100)
        const isHighConfidence = sample.confidence >= 0.8

        return (
          <div
            key={idx}
            className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm mb-3"
          >
            {/* Arabic text */}
            <p className="text-right font-tajawal text-sm leading-relaxed text-gray-800 mb-3">
              {truncateText(sample.text)}
            </p>

            {/* Metadata row */}
            <div className="flex items-center gap-2 mb-3 flex-row-reverse">
              <span className="bg-gray-100 text-gray-600 px-2 py-0.5 rounded text-xs font-tajawal">
                {sample.source_dataset}
              </span>
              <span className="text-xs text-gray-400 font-tajawal">
                {`الحكم الحقيقي: ${sample.ground_truth}`}
              </span>
            </div>

            {/* Confidence bar */}
            <div className="mb-1">
              <div className="h-2 w-full rounded-full bg-gray-200">
                <div
                  className={`h-2 rounded-full ${confidenceBarColor(sample.confidence)}`}
                  style={{ width: `${confidencePct}%` }}
                />
              </div>
              <p className="text-xs text-gray-400 font-tajawal mt-1">
                {`الثقة: ${toArabicDigits(confidencePct)}٪`}
              </p>
            </div>

            {/* High-confidence warning */}
            {isHighConfidence && (
              <p className="text-xs text-red-600 font-medium font-tajawal mt-1">
                {'⚠ ثقة عالية — خطأ مقلق'}
              </p>
            )}
          </div>
        )
      })}

      {samples.length > MAX_DISPLAY && (
        <p className="text-xs text-gray-400 font-tajawal text-center mt-2">
          {`يُعرض ${toArabicDigits(MAX_DISPLAY)} من أصل ${toArabicDigits(samples.length)} إيجابية كاذبة`}
        </p>
      )}
    </div>
  )
}
