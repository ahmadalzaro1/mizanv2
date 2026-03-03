import type { ReactNode } from 'react'

interface TweetCardProps {
  text: string
  sourceDataset: string
  dialect: string | null
  highlights?: {
    words: string[]
    type: 'hate' | 'not_hate'
  }
}

/** Strip Arabic diacritics (tashkeel) for matching — display preserves original. */
function stripDiacritics(s: string): string {
  return s.normalize('NFD').replace(/[\u064B-\u065F\u0670]/g, '')
}

function highlightText(
  text: string,
  words: string[],
  className: string
): ReactNode {
  if (words.length === 0) return text

  const normalizedText = stripDiacritics(text)
  const normalizedWords = words.map(stripDiacritics)

  const escaped = normalizedWords.map(w => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
  const pattern = new RegExp(`(${escaped.join('|')})`, 'g')

  const parts: ReactNode[] = []
  let lastIndex = 0
  let match: RegExpExecArray | null

  while ((match = pattern.exec(normalizedText)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index))
    }
    const matchEnd = match.index + match[0].length
    parts.push(
      <mark key={match.index} className={className}>
        {text.slice(match.index, matchEnd)}
      </mark>
    )
    lastIndex = matchEnd
  }
  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex))
  }

  return parts.length > 0 ? parts : text
}

export default function TweetCard({ text, sourceDataset, dialect, highlights }: TweetCardProps) {
  const highlightClass = highlights?.type === 'hate'
    ? 'bg-amber-200 text-amber-900 rounded px-0.5'
    : 'bg-green-200 text-green-900 rounded px-0.5'

  return (
    <div className="rounded-xl bg-white p-6 shadow-sm">
      <p
        dir="rtl"
        className="font-tajawal text-2xl leading-relaxed text-gray-900"
      >
        {highlights
          ? highlightText(text, highlights.words, highlightClass)
          : text}
      </p>

      <div className="mt-4 flex items-center gap-2">
        <span className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-500">
          {sourceDataset}
        </span>
        {dialect && (
          <span className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-500">
            {dialect}
          </span>
        )}
      </div>
    </div>
  )
}
