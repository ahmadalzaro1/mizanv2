import { api } from './api'
import type { TrainingSession, SessionItem } from './types'

export async function createSession(): Promise<TrainingSession> {
  const res = await api.post<TrainingSession>('/api/training/sessions')
  return res.data
}

export async function getSession(sessionId: string): Promise<TrainingSession> {
  const res = await api.get<TrainingSession>(`/api/training/sessions/${sessionId}`)
  return res.data
}

export async function submitLabel(
  sessionId: string,
  itemId: string,
  label: { moderator_label: 'hate' | 'not_hate'; moderator_hate_type?: string }
): Promise<SessionItem> {
  const res = await api.put<SessionItem>(
    `/api/training/sessions/${sessionId}/items/${itemId}`,
    label
  )
  return res.data
}

export async function listSessions(): Promise<TrainingSession[]> {
  const res = await api.get<{ sessions: TrainingSession[] }>('/api/training/sessions')
  return res.data.sessions
}

export async function streamExplanation(
  sessionId: string,
  itemId: string,
  onToken: (token: string, meta?: { cached?: boolean; fallback?: boolean }) => void,
  onDone: (meta?: { fallback?: boolean }) => void,
): Promise<void> {
  const baseUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
  const token = localStorage.getItem('mizan_token')

  const response = await fetch(
    `${baseUrl}/api/training/sessions/${sessionId}/items/${itemId}/explanation-stream`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  )

  if (!response.ok) throw new Error(`Explanation stream failed: ${response.status}`)

  const reader = response.body!.getReader()
  const decoder = new TextDecoder()
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
          if (data.done) {
            onDone({ fallback: data.fallback })
            return
          }
          if (data.token) {
            onToken(data.token, { cached: data.cached, fallback: data.fallback })
          }
        } catch {
          // ignore partial JSON
        }
      }
    }
  }
}
