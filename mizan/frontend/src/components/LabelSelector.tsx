import { useState, useEffect } from 'react'
import { HATE_CATEGORIES } from '../lib/types'

interface LabelSelectorProps {
  onSubmit: (label: 'hate' | 'not_hate', hateType?: string) => void
  disabled?: boolean
  initialLabel?: 'hate' | 'not_hate' | null
  initialHateType?: string | null
}

export default function LabelSelector({
  onSubmit,
  disabled = false,
  initialLabel = null,
  initialHateType = null,
}: LabelSelectorProps) {
  const [selectedLabel, setSelectedLabel] = useState<'hate' | 'not_hate' | null>(
    initialLabel ?? null
  )
  const [selectedCategory, setSelectedCategory] = useState<string | null>(
    initialHateType ?? null
  )

  useEffect(() => {
    setSelectedLabel(initialLabel ?? null)
    setSelectedCategory(initialHateType ?? null)
  }, [initialLabel, initialHateType])

  function handleLabelClick(label: 'hate' | 'not_hate') {
    setSelectedLabel(label)
    if (label === 'not_hate') {
      setSelectedCategory(null)
    }
  }

  function handleCategoryClick(value: string) {
    setSelectedCategory(value)
  }

  function handleSubmit() {
    if (!selectedLabel) return
    if (selectedLabel === 'hate' && !selectedCategory) return
    onSubmit(selectedLabel, selectedCategory ?? undefined)
  }

  const canSubmit =
    !disabled &&
    selectedLabel !== null &&
    (selectedLabel === 'not_hate' || selectedCategory !== null)

  return (
    <div dir="rtl" className="font-tajawal">
      {/* Step 1: Hate / Not Hate */}
      <div className="mb-4 grid grid-cols-2 gap-3">
        <button
          type="button"
          disabled={disabled}
          onClick={() => handleLabelClick('hate')}
          className={`rounded-lg border-2 px-4 py-4 text-lg font-bold transition-colors ${
            selectedLabel === 'hate'
              ? 'border-red-500 bg-red-100 text-red-800'
              : 'border-red-300 bg-red-50 text-red-700 hover:bg-red-100'
          } disabled:cursor-not-allowed disabled:opacity-50`}
        >
          خطاب كراهية
        </button>

        <button
          type="button"
          disabled={disabled}
          onClick={() => handleLabelClick('not_hate')}
          className={`rounded-lg border-2 px-4 py-4 text-lg font-bold transition-colors ${
            selectedLabel === 'not_hate'
              ? 'border-green-500 bg-green-100 text-green-800'
              : 'border-green-300 bg-green-50 text-green-700 hover:bg-green-100'
          } disabled:cursor-not-allowed disabled:opacity-50`}
        >
          ليس كراهية
        </button>
      </div>

      {/* Step 2: Category selection (hate only) */}
      {selectedLabel === 'hate' && (
        <div className="mb-4 grid grid-cols-3 gap-2">
          {HATE_CATEGORIES.map((cat) => (
            <button
              key={cat.value}
              type="button"
              disabled={disabled}
              onClick={() => handleCategoryClick(cat.value)}
              className={`rounded-lg border-2 px-3 py-3 text-sm font-semibold transition-colors ${
                selectedCategory === cat.value
                  ? 'border-mizan-navy bg-blue-50 text-mizan-navy'
                  : 'border-gray-200 bg-white text-gray-700 hover:border-gray-400'
              } disabled:cursor-not-allowed disabled:opacity-50`}
            >
              {cat.label}
            </button>
          ))}
        </div>
      )}

      {/* Submit button */}
      <button
        type="button"
        disabled={!canSubmit}
        onClick={handleSubmit}
        className="w-full rounded-lg bg-mizan-navy px-4 py-3 text-lg font-bold text-white transition-colors hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
      >
        إرسال
      </button>
    </div>
  )
}
