import { toArabicDigits } from '../lib/format'

interface CalibrationScoreProps {
  correctCount: number
  labeledCount: number
}

export default function CalibrationScore({ correctCount, labeledCount }: CalibrationScoreProps) {
  if (labeledCount === 0) {
    return (
      <div dir="rtl" className="rounded-lg bg-gray-50 px-4 py-2 text-center font-tajawal text-sm text-gray-400">
        ستظهر نسبة المعايرة بعد أول تصنيف
      </div>
    )
  }

  const percentage = Math.round((correctCount / labeledCount) * 100)

  let colorClass: string
  if (percentage >= 80) {
    colorClass = 'bg-green-100 text-green-800'
  } else if (percentage >= 60) {
    colorClass = 'bg-amber-100 text-amber-800'
  } else {
    colorClass = 'bg-red-100 text-red-800'
  }

  return (
    <div dir="rtl" className={`flex items-center justify-between rounded-lg px-4 py-2 font-tajawal transition-all duration-300 ${colorClass}`}>
      <span className="text-sm font-bold">
        نسبة المعايرة: {toArabicDigits(percentage)}٪
      </span>
      <span className="text-xs opacity-75">
        {toArabicDigits(correctCount)} من {toArabicDigits(labeledCount)} صحيح
      </span>
    </div>
  )
}
