import { toArabicDigits } from '../lib/format'

interface ProgressBarProps {
  current: number
  total: number
  labeled: number
}

export default function ProgressBar({ current, total, labeled }: ProgressBarProps) {
  const percent = total > 0 ? Math.round((current / total) * 100) : 0

  return (
    <div className="w-full">
      <div className="mb-1 flex items-center justify-between font-tajawal text-sm text-gray-600">
        <span dir="rtl">
          {toArabicDigits(current)} من {toArabicDigits(total)}
        </span>
        <span dir="rtl">
          تم تصنيف {toArabicDigits(labeled)}
        </span>
      </div>

      <div className="h-3 w-full overflow-hidden rounded-full bg-gray-200">
        <div
          className="h-full rounded-full bg-mizan-navy transition-all duration-300"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  )
}
