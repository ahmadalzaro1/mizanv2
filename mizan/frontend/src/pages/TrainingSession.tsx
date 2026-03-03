import { useState, useEffect, useCallback, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getSession, submitLabel, streamExplanation } from '../lib/training-api'
import type { TrainingSession as TrainingSessionType, SessionItem } from '../lib/types'
import TweetCard from '../components/TweetCard'
import ProgressBar from '../components/ProgressBar'
import CalibrationScore from '../components/CalibrationScore'
import LabelSelector from '../components/LabelSelector'
import FeedbackReveal from '../components/FeedbackReveal'

export default function TrainingSessionPage() {
  const { sessionId } = useParams()
  const navigate = useNavigate()

  const [session, setSession] = useState<TrainingSessionType | null>(null)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isChangingAnswer, setIsChangingAnswer] = useState(false)

  // Phase 10: streaming explanation state
  const [streamedExplanation, setStreamedExplanation] = useState<string | null>(null)
  const [isExplanationStreaming, setIsExplanationStreaming] = useState(false)
  const [isLLMExplanation, setIsLLMExplanation] = useState<boolean | undefined>(undefined)
  const streamedRef = useRef<string>('')

  useEffect(() => {
    let cancelled = false
    getSession(sessionId!)
      .then((data) => {
        if (cancelled) return
        setSession(data)
        const items = data.items ?? []
        const firstUnlabeled = items.findIndex((i) => i.moderator_label === null)
        if (firstUnlabeled === -1 && items.length > 0) {
          navigate(`/train/sessions/${data.id}/summary`, { replace: true })
          return
        }
        if (firstUnlabeled > 0) {
          setCurrentIndex(firstUnlabeled)
        }
      })
      .catch(() => {
        if (!cancelled) navigate('/train', { replace: true })
      })
    return () => {
      cancelled = true
    }
  }, [sessionId, navigate])

  const items = session?.items ?? []
  const currentItem = items[currentIndex] as SessionItem | undefined
  const labeledCount = items.filter((i) => i.moderator_label !== null).length
  const correctCount = items.filter((i) => i.is_correct === true).length
  const isItemLabeled = currentItem?.moderator_label !== null && currentItem?.moderator_label !== undefined

  const allLabeled = items.length > 0 && items.every((i) => i.moderator_label !== null)

  const canGoForward = useCallback((): boolean => {
    if (!currentItem) return false
    if (currentItem.moderator_label === null) return false
    if (currentIndex === items.length - 1 && allLabeled) return true
    if (currentIndex === items.length - 1 && !allLabeled) return false
    return true
  }, [currentItem, currentIndex, items.length, allLabeled])

  function handleSubmit(label: 'hate' | 'not_hate', hateType?: string) {
    if (!session || !currentItem) return
    setIsSubmitting(true)
    setError(null)

    submitLabel(session.id, currentItem.id, {
      moderator_label: label,
      moderator_hate_type: hateType,
    })
      .then((updatedItem) => {
        setSession((prev) => {
          if (!prev || !prev.items) return prev
          const updatedItems = prev.items.map((item) =>
            item.id === updatedItem.id ? updatedItem : item
          )
          const newLabeledCount = updatedItems.filter(
            (i) => i.moderator_label !== null
          ).length
          const isNowComplete = newLabeledCount === prev.total_items
          const correctCount = isNowComplete
            ? updatedItems.filter((i) => i.is_correct === true).length
            : prev.correct_count
          return {
            ...prev,
            items: updatedItems,
            labeled_count: newLabeledCount,
            status: isNowComplete ? 'completed' as const : prev.status,
            correct_count: correctCount,
            completed_at: isNowComplete ? new Date().toISOString() : prev.completed_at,
          }
        })
        setIsChangingAnswer(false)

        // Phase 10: trigger explanation stream after label submission
        setStreamedExplanation(null)
        streamedRef.current = ''
        setIsExplanationStreaming(true)
        setIsLLMExplanation(undefined)

        streamExplanation(
          session!.id,
          updatedItem.id,
          (token, meta) => {
            if (meta?.cached) {
              // Cached explanation — show immediately, mark as not-streaming
              streamedRef.current = token
              setStreamedExplanation(token)
              setIsExplanationStreaming(false)
              setIsLLMExplanation(false) // cached = previously generated
            } else {
              streamedRef.current += token
              setStreamedExplanation(streamedRef.current)
              if (meta?.fallback) {
                setIsLLMExplanation(false)
              } else {
                setIsLLMExplanation(true)
              }
            }
          },
          (meta) => {
            setIsExplanationStreaming(false)
            if (meta?.fallback) {
              setIsLLMExplanation(false)
            }
            // Update item in local state so revisiting shows cached text
            const accumulated = streamedRef.current
            setSession((prev) => {
              if (!prev?.items) return prev
              return {
                ...prev,
                items: prev.items.map((item) =>
                  item.id === updatedItem.id
                    ? { ...item, ai_explanation_text: accumulated || item.ai_explanation_text }
                    : item
                ),
              }
            })
          }
        ).catch(() => {
          setIsExplanationStreaming(false)
        })
      })
      .catch(() => {
        setError('\u062d\u062f\u062b \u062e\u0637\u0623 \u0623\u062b\u0646\u0627\u0621 \u0627\u0644\u062d\u0641\u0638')
      })
      .finally(() => {
        setIsSubmitting(false)
      })
  }

  function handlePrevious() {
    setStreamedExplanation(null)
    setIsExplanationStreaming(false)
    setIsLLMExplanation(undefined)
    streamedRef.current = ''
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1)
      setIsChangingAnswer(false)
    }
  }

  function handleNext() {
    setStreamedExplanation(null)
    setIsExplanationStreaming(false)
    setIsLLMExplanation(undefined)
    streamedRef.current = ''
    if (!currentItem || currentItem.moderator_label === null) return

    if (currentIndex === items.length - 1 && allLabeled) {
      navigate(`/train/sessions/${session!.id}/summary`)
      return
    }

    if (currentIndex < items.length - 1) {
      setCurrentIndex(currentIndex + 1)
      setIsChangingAnswer(false)
    }
  }

  if (!session || !currentItem) {
    return (
      <div className="flex items-center justify-center py-20">
        <p className="font-tajawal text-lg text-gray-500">
          {'\u062c\u0627\u0631\u064d \u0627\u0644\u062a\u062d\u0645\u064a\u0644...'}
        </p>
      </div>
    )
  }

  return (
    <div>
      <ProgressBar
        current={currentIndex + 1}
        total={items.length}
        labeled={labeledCount}
      />

      <div className="mt-3">
        <CalibrationScore
          correctCount={correctCount}
          labeledCount={labeledCount}
        />
      </div>

      <div className="mt-6">
        <TweetCard
          text={currentItem.content_example.text}
          sourceDataset={currentItem.content_example.source_dataset}
          dialect={currentItem.content_example.dialect}
          highlights={
            isItemLabeled && !isChangingAnswer && currentItem.ai_trigger_words
              ? {
                  words: currentItem.ai_trigger_words.map(tw => tw.token),
                  type: currentItem.ai_label === 'hate' ? 'hate' : 'not_hate',
                }
              : undefined
          }
        />
      </div>

      <div className="mt-6">
        {isItemLabeled && !isChangingAnswer ? (
          <>
            <FeedbackReveal
              moderatorLabel={currentItem.moderator_label!}
              moderatorHateType={currentItem.moderator_hate_type}
              groundTruthLabel={currentItem.ground_truth_label ?? ''}
              groundTruthHateType={currentItem.ground_truth_hate_type}
              isCorrect={currentItem.is_correct ?? false}
              onNext={handleNext}
              onPrevious={handlePrevious}
              canGoBack={currentIndex > 0}
              canGoForward={canGoForward()}
              aiExplanationText={currentItem.ai_explanation_text}
              streamedExplanation={streamedExplanation}
              isStreaming={isExplanationStreaming}
              isLLMExplanation={isLLMExplanation}
            />
            <div className="mt-3 text-center">
              <button
                type="button"
                onClick={() => setIsChangingAnswer(true)}
                className="text-sm text-mizan-navy underline hover:opacity-70"
              >
                {'\u062a\u063a\u064a\u064a\u0631 \u0627\u0644\u0625\u062c\u0627\u0628\u0629'}
              </button>
            </div>
          </>
        ) : (
          <>
            <LabelSelector
              onSubmit={handleSubmit}
              disabled={isSubmitting}
              initialLabel={isChangingAnswer ? currentItem.moderator_label : null}
              initialHateType={isChangingAnswer ? currentItem.moderator_hate_type : null}
            />
            {isChangingAnswer && (
              <div className="mt-3 text-center">
                <button
                  type="button"
                  onClick={() => setIsChangingAnswer(false)}
                  className="text-sm text-gray-500 underline hover:opacity-70"
                >
                  {'\u0625\u0644\u063a\u0627\u0621'}
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {error && (
        <div className="mt-4 rounded-lg bg-red-50 p-3 text-center text-sm text-red-700">
          {error}
        </div>
      )}
    </div>
  )
}
