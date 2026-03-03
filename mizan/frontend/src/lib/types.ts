export type UserRole = 'super_admin' | 'admin' | 'moderator'

export type SamplingStrategy = 'sequential' | 'uncertainty' | 'disagreement'

export const STRATEGY_LABELS: Record<SamplingStrategy, string> = {
  sequential: 'تدريب تسلسلي',
  uncertainty: 'تدريب التحدي',
  disagreement: 'أمثلة مثيرة للجدل',
}

export interface User {
  id: string
  email: string
  full_name: string
  role: UserRole
  institution_id: string | null
}

export interface ContentExampleBrief {
  id: string
  text: string
  source_dataset: string
  dialect: string | null
}

export interface TriggerWord {
  token: string
  score: number
}

export interface SessionItem {
  id: string
  position: number
  content_example: ContentExampleBrief
  moderator_label: 'hate' | 'not_hate' | null
  moderator_hate_type: string | null
  is_correct: boolean | null
  ground_truth_label: string | null
  ground_truth_hate_type: string | null
  labeled_at: string | null
  // Phase 5: AI explanation
  ai_label: string | null
  ai_confidence: number | null
  ai_explanation_text: string | null
  ai_trigger_words: TriggerWord[] | null
}

export interface TrainingSession {
  id: string
  status: 'in_progress' | 'completed'
  total_items: number
  labeled_count: number
  correct_count: number | null
  created_at: string
  completed_at: string | null
  strategy: SamplingStrategy
  items?: SessionItem[]
}

export const HATE_CATEGORIES = [
  { value: 'race', label: 'عنصرية' },
  { value: 'religion', label: 'ديني' },
  { value: 'ideology', label: 'أيديولوجي' },
  { value: 'gender', label: 'جنساني' },
  { value: 'disability', label: 'إعاقة' },
  { value: 'social_class', label: 'طبقي' },
  { value: 'tribalism', label: 'عشائري' },
  { value: 'refugee_related', label: 'لاجئين' },
  { value: 'political_affiliation', label: 'سياسي' },
] as const
