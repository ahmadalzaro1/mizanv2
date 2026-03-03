import { api } from './api'

export interface CategoryMetrics {
  category: string
  category_ar: string
  sample_count: number
  tp: number
  fp: number
  fn: number
  precision: number
  recall: number
  f1: number
  confidence_scores?: number[]
}

export interface OverallMetrics {
  precision: number
  recall: number
  f1: number
  total: number
  tp: number
  fp: number
  fn: number
  tn: number
}

export interface SourceMetrics {
  source: string
  total: number
  precision: number
  recall: number
  f1: number
  false_positive_rate: number
}

export interface FalsePositiveSample {
  text: string
  source_dataset: string
  confidence: number
  ground_truth: string
}

export interface ConfidenceDist {
  scores: number[]
  count: number
}

export interface AuditResults {
  overall: OverallMetrics
  per_category: CategoryMetrics[]
  per_source?: SourceMetrics[]
  confidence_dist?: Record<string, ConfidenceDist>
  false_positives?: FalsePositiveSample[]
}

export interface AuditRun {
  id: string
  computed_at: string
  total_examples: number
  duration_ms: number
  results: AuditResults
}

export interface StreamProgress {
  progress: number
  current: number
  total: number
}

export type StreamCallback = (data: StreamProgress) => void

export async function runAudit(): Promise<AuditRun> {
  const { data } = await api.post('/api/audit/run')
  return data
}

export async function getAuditResults(): Promise<AuditRun> {
  const { data } = await api.get('/api/audit/results')
  return data
}

export async function downloadAuditCsv(): Promise<Blob> {
  const { data } = await api.get('/api/audit/results/csv', { responseType: 'blob' })
  return data
}

export async function runAuditStream(
  onProgress: StreamCallback
): Promise<AuditRun> {
  const baseUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
  const token = localStorage.getItem('mizan_token')

  const response = await fetch(`${baseUrl}/api/audit/run/stream`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`Audit stream failed: ${response.status}`)
  }

  const reader = response.body!.getReader()
  const decoder = new TextDecoder()
  let result: AuditRun | null = null
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6))
          if (data.error) {
            throw new Error(data.error)
          }
          if (data.done) {
            result = {
              id: data.id,
              computed_at: data.computed_at,
              total_examples: data.total_examples,
              duration_ms: data.duration_ms,
              results: data.results,
            }
          } else if (data.progress !== undefined) {
            onProgress({
              progress: data.progress,
              current: data.current,
              total: data.total,
            })
          }
        } catch (e) {
          if (e instanceof SyntaxError) continue
          throw e
        }
      }
    }
  }

  if (!result) {
    throw new Error('Audit stream ended without results')
  }
  return result
}

export async function streamInsight(
  onToken: (token: string) => void,
): Promise<string> {
  const baseUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
  const token = localStorage.getItem('mizan_token')

  const response = await fetch(`${baseUrl}/api/audit/results/insight-stream`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  if (!response.ok) throw new Error(`Insight stream failed: ${response.status}`)

  const reader = response.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let fullText = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6))
          if (data.error) throw new Error(data.error)
          if (data.done) return fullText
          if (data.token) {
            fullText += data.token
            onToken(data.token)
          }
        } catch (e) {
          if (e instanceof SyntaxError) continue
          throw e
        }
      }
    }
  }

  return fullText
}
