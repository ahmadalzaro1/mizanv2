import AIExplanation from './AIExplanation'

const LABEL_AR: Record<string, string> = {
  hate: 'خطاب كراهية',
  not_hate: 'ليس كراهية',
  offensive: 'محتوى مسيء',
  spam: 'محتوى مزعج',
}

const HATE_TYPE_AR: Record<string, string> = {
  race: 'عنصرية',
  religion: 'ديني',
  ideology: 'أيديولوجي',
  gender: 'جنساني',
  disability: 'إعاقة',
  social_class: 'طبقي',
  tribalism: 'عشائري',
  refugee_related: 'لاجئين',
  political_affiliation: 'سياسي',
  unknown: 'غير محدد',
}

interface FeedbackRevealProps {
  moderatorLabel: 'hate' | 'not_hate'
  moderatorHateType: string | null
  groundTruthLabel: string
  groundTruthHateType: string | null
  isCorrect: boolean
  onNext: () => void
  onPrevious: () => void
  canGoBack: boolean
  canGoForward: boolean
  aiExplanationText: string | null
  // Phase 10: streaming
  streamedExplanation?: string | null
  isStreaming?: boolean
  isLLMExplanation?: boolean
}

function formatLabel(label: string, hateType: string | null): string {
  const labelText = LABEL_AR[label] ?? label
  if (hateType) {
    const typeText = HATE_TYPE_AR[hateType] ?? hateType
    return `${labelText} - ${typeText}`
  }
  return labelText
}

export default function FeedbackReveal({
  moderatorLabel,
  moderatorHateType,
  groundTruthLabel,
  groundTruthHateType,
  isCorrect,
  onNext,
  onPrevious,
  canGoBack,
  canGoForward,
  aiExplanationText,
  streamedExplanation,
  isStreaming,
  isLLMExplanation,
}: FeedbackRevealProps) {
  return (
    <div dir="rtl" className="font-tajawal">
      {/* Correct / Incorrect banner */}
      <div
        className={`mb-4 rounded-lg px-4 py-3 text-center text-lg font-bold ${
          isCorrect
            ? 'bg-green-100 text-green-800'
            : 'bg-red-100 text-red-800'
        }`}
      >
        {isCorrect ? (
          <span>&#10003; صحيح!</span>
        ) : (
          <span>&#10007; غير صحيح</span>
        )}
      </div>

      {/* Your answer */}
      <div className="mb-3 rounded-lg border border-gray-200 bg-white p-4">
        <p className="mb-1 text-sm text-gray-500">إجابتك</p>
        <p className="text-base font-semibold text-gray-900">
          {formatLabel(moderatorLabel, moderatorHateType)}
        </p>
      </div>

      {/* Correct answer */}
      <div className="mb-6 rounded-lg border border-gray-200 bg-white p-4">
        <p className="mb-1 text-sm text-gray-500">الإجابة الصحيحة</p>
        <p className="text-base font-semibold text-gray-900">
          {formatLabel(groundTruthLabel, groundTruthHateType)}
        </p>
      </div>

      {/* AI Explanation — Phase 10: streaming-aware */}
      {(aiExplanationText || streamedExplanation || isStreaming) ? (
        <div className="mb-6">
          <AIExplanation
            explanationText={streamedExplanation ?? aiExplanationText}
            isStreaming={isStreaming}
            isLLM={isLLMExplanation}
          />
        </div>
      ) : (
        <div dir="rtl" className="mb-6 rounded-lg border border-gray-200 bg-gray-50 p-3 font-tajawal">
          <p className="text-center text-sm text-gray-500">النموذج غير جاهز بعد</p>
        </div>
      )}

      {/* Navigation */}
      <div className="flex gap-3">
        <button
          type="button"
          disabled={!canGoBack}
          onClick={onPrevious}
          className="flex-1 rounded-lg border-2 border-gray-300 bg-white px-4 py-3 text-base font-bold text-gray-700 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
        >
          السابق
        </button>
        <button
          type="button"
          disabled={!canGoForward}
          onClick={onNext}
          className="flex-1 rounded-lg bg-mizan-navy px-4 py-3 text-base font-bold text-white transition-colors hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
        >
          التالي
        </button>
      </div>
    </div>
  )
}
