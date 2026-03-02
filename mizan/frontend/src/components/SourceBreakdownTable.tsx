import type { SourceMetrics } from '../lib/audit-api'
import { toArabicDigits } from '../lib/format'

interface SourceBreakdownTableProps {
  sources: SourceMetrics[]
}

function formatPct(value: number): string {
  return toArabicDigits(Math.round(value * 100)) + '٪'
}

function f1CellClass(f1: number): string {
  if (f1 >= 0.7) return 'bg-green-100 text-green-800'
  if (f1 >= 0.5) return 'bg-amber-100 text-amber-800'
  return 'bg-red-100 text-red-800'
}

function fprCellClass(fpr: number): string {
  if (fpr <= 0.1) return 'bg-green-100 text-green-800'
  if (fpr <= 0.2) return 'bg-amber-100 text-amber-800'
  return 'bg-red-100 text-red-800'
}

export default function SourceBreakdownTable({ sources }: SourceBreakdownTableProps) {
  if (sources.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <p className="text-gray-400 font-tajawal text-sm">لا توجد بيانات لمصادر البيانات</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table
        className="w-full text-right font-tajawal"
        style={{ borderCollapse: 'collapse' }}
        dir="rtl"
      >
        <thead>
          <tr className="bg-gray-50 border-b border-gray-200">
            <th className="px-4 py-3 text-sm text-gray-500 font-medium">مصدر البيانات</th>
            <th className="px-4 py-3 text-sm text-gray-500 font-medium">عدد الأمثلة</th>
            <th className="px-4 py-3 text-sm text-gray-500 font-medium">F1</th>
            <th className="px-4 py-3 text-sm text-gray-500 font-medium">الدقة</th>
            <th className="px-4 py-3 text-sm text-gray-500 font-medium">الاسترجاع</th>
            <th className="px-4 py-3 text-sm text-gray-500 font-medium">معدل الإيجابيات الكاذبة</th>
          </tr>
        </thead>
        <tbody>
          {sources.map((src, idx) => (
            <tr
              key={src.source}
              className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
            >
              <td className="px-4 py-3 text-sm font-medium text-mizan-navy">
                {src.source}
              </td>
              <td className="px-4 py-3 text-sm text-gray-700">
                {toArabicDigits(src.total)}
              </td>
              <td className="px-4 py-3">
                <span
                  className={`inline-block px-2 py-0.5 rounded text-sm font-medium ${f1CellClass(src.f1)}`}
                >
                  {formatPct(src.f1)}
                </span>
              </td>
              <td className="px-4 py-3 text-sm text-gray-700">
                {formatPct(src.precision)}
              </td>
              <td className="px-4 py-3 text-sm text-gray-700">
                {formatPct(src.recall)}
              </td>
              <td className="px-4 py-3">
                <span
                  className={`inline-block px-2 py-0.5 rounded text-sm font-medium ${fprCellClass(src.false_positive_rate)}`}
                >
                  {formatPct(src.false_positive_rate)}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
