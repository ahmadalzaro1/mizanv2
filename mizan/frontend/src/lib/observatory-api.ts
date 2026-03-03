import { api } from './api'

export interface MonthlyData {
  year: number
  month: number
  hate_count: number
  total_count: number
}

export interface HistoricalEvent {
  year: number
  month: number
  label_ar: string
  label_en: string
}

export interface TrendsResponse {
  monthly: MonthlyData[]
  events: HistoricalEvent[]
}

export async function getTrends(): Promise<TrendsResponse> {
  const { data } = await api.get('/api/observatory/trends')
  return data
}
