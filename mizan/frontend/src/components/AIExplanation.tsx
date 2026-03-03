interface AIExplanationProps {
  explanationText: string | null
  isStreaming?: boolean
  isLLM?: boolean
}

export default function AIExplanation({ explanationText, isStreaming, isLLM }: AIExplanationProps) {
  return (
    <div dir="rtl" className="rounded-lg border border-blue-200 bg-blue-50 p-4 font-tajawal">
      <div className="mb-2 flex items-center gap-2">
        <svg className="h-5 w-5 text-blue-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" />
        </svg>
        <h3 className="text-sm font-bold text-blue-800">تفسير النموذج</h3>
        {isLLM !== undefined && (
          <span className="text-xs text-blue-400">
            {isLLM ? '(ذكاء اصطناعي)' : '(قالب)'}
          </span>
        )}
      </div>
      {isStreaming && !explanationText ? (
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
          <span className="text-sm text-blue-500">جارٍ التفسير...</span>
        </div>
      ) : (
        <p className="text-base leading-relaxed text-blue-900">
          {explanationText}
          {isStreaming && (
            <span className="inline-block h-4 w-1 animate-pulse bg-blue-600 ms-1" />
          )}
        </p>
      )}
    </div>
  )
}
