import { useState, useEffect } from 'react'
import { getAuditResults, runAudit, runAuditStream, downloadAuditCsv, streamInsight } from '../lib/audit-api'
import type { AuditRun, AuditResults } from '../lib/audit-api'
import BiasChart from '../components/BiasChart'
import ConfidenceHistogram from '../components/ConfidenceHistogram'
import SourceBreakdownTable from '../components/SourceBreakdownTable'
import FalsePositiveList from '../components/FalsePositiveList'
import { toArabicDigits } from '../lib/format'

const TABS = [
  { id: 'overview' as const, label: 'نظرة عامة' },
  { id: 'confidence' as const, label: 'توزيع الثقة' },
  { id: 'sources' as const, label: 'مصادر البيانات' },
  { id: 'falsepos' as const, label: 'الإيجابيات الكاذبة' },
]
type TabId = (typeof TABS)[number]['id']

const CATEGORY_LABELS_AR: Record<string, string> = {
  race: 'عنصرية',
  religion: 'ديني',
  ideology: 'أيديولوجي',
  gender: 'جنساني',
  disability: 'إعاقة',
  social_class: 'طبقي',
  tribalism: 'عشائري',
  refugee_related: 'لاجئين',
  political_affiliation: 'سياسي',
  unknown: 'غير مصنف',
}

function generateInsight(results: AuditResults): string {
  const { overall, per_category, per_source, false_positives } = results
  const sentences: string[] = []

  // 1. Overall F1 assessment
  const f1Pct = Math.round(overall.f1 * 100)
  if (f1Pct >= 80) {
    sentences.push(
      `يحقق النموذج أداءً جيداً بشكل عام بمعدل F1 يبلغ ${toArabicDigits(f1Pct)}٪.`
    )
  } else if (f1Pct >= 60) {
    sentences.push(
      `أداء النموذج متوسط بمعدل F1 يبلغ ${toArabicDigits(f1Pct)}٪، مع مجال للتحسين.`
    )
  } else {
    sentences.push(
      `أداء النموذج ضعيف بمعدل F1 يبلغ ${toArabicDigits(f1Pct)}٪ ويحتاج إلى تحسين كبير.`
    )
  }

  // 2. Weakest category
  const categoriesWithSamples = (per_category ?? []).filter((c) => c.sample_count > 0)
  if (categoriesWithSamples.length > 0) {
    const weakest = categoriesWithSamples.reduce((a, b) => (a.f1 < b.f1 ? a : b))
    sentences.push(
      `أضعف فئة هي "${weakest.category_ar}" بمعدل F1 يبلغ ${toArabicDigits(Math.round(weakest.f1 * 100))}٪ فقط (${toArabicDigits(weakest.sample_count)} عينة).`
    )
  }

  // 3. False positive rate or hardest data source
  if (per_source && per_source.length > 0) {
    const hardest = per_source.reduce((a, b) => (a.f1 < b.f1 ? a : b))
    sentences.push(
      `أصعب مصدر بيانات هو ${hardest.source} بمعدل F1 يبلغ ${toArabicDigits(Math.round(hardest.f1 * 100))}٪.`
    )
  } else if (false_positives && false_positives.length > 0) {
    sentences.push(
      `تم رصد ${toArabicDigits(false_positives.length)} حالة إيجابية كاذبة حيث صنّف النموذج محتوى غير مؤذٍ على أنه كراهية.`
    )
  }

  return sentences.join(' ')
}

export default function BiasAuditorPage() {
  const [auditRun, setAuditRun] = useState<AuditRun | null>(null)
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<TabId>('overview')

  // Phase 10: LLM insight streaming state
  const [insightText, setInsightText] = useState<string | null>(null)
  const [isInsightStreaming, setIsInsightStreaming] = useState(false)

  useEffect(() => {
    getAuditResults()
      .then(setAuditRun)
      .catch(() => {
        // No cached run — that's ok, user can trigger one
      })
      .finally(() => setLoading(false))
  }, [])

  async function fetchInsight() {
    setInsightText(null)
    setIsInsightStreaming(true)
    try {
      await streamInsight((token) => {
        setInsightText((prev) => (prev ?? '') + token)
      })
    } catch {
      // Fallback to frontend template
      if (auditRun?.results) {
        setInsightText(generateInsight(auditRun.results))
      }
    } finally {
      setIsInsightStreaming(false)
    }
  }

  useEffect(() => {
    if (auditRun?.results) {
      fetchInsight()
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [auditRun?.id])

  async function handleRunAudit() {
    setRunning(true)
    setProgress(0)
    setError(null)
    try {
      const result = await runAuditStream((data) => {
        setProgress(data.progress)
      })
      setAuditRun(result)
    } catch {
      // Fallback to non-streaming run
      try {
        const result = await runAudit()
        setAuditRun(result)
      } catch {
        setError('حدث خطأ أثناء تشغيل التدقيق. تأكد من تحميل النموذج.')
      }
    } finally {
      setRunning(false)
      setProgress(0)
    }
  }

  function handleDownloadCsv() {
    downloadAuditCsv().then((blob) => {
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'mizan-bias-audit.csv'
      a.click()
      URL.revokeObjectURL(url)
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <p className="font-tajawal text-lg text-gray-500">جارٍ التحميل...</p>
      </div>
    )
  }

  const results = auditRun?.results
  const overall = results?.overall
  const perCategory = results?.per_category ?? []

  // Find weakest categories (F1 < 0.5)
  const weakCategories = perCategory.filter((c) => c.sample_count > 0 && c.f1 < 0.5)

  return (
    <div dir="rtl" className="font-tajawal">
      {/* Header */}
      <h2 className="mb-2 text-2xl font-bold text-mizan-navy">
        مدقق التحيز — أداء نموذج MARBERT
      </h2>
      <p className="mb-6 text-gray-500">
        تقييم عدالة النموذج حسب فئات خطاب الكراهية التسع
      </p>

      {/* Run / Re-run + CSV buttons (pinned above tabs) */}
      <div className="mb-4 flex items-center gap-4">
        <button
          type="button"
          onClick={handleRunAudit}
          disabled={running}
          className="rounded-lg bg-mizan-navy px-6 py-2 font-bold text-white transition-colors hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {running ? 'جارٍ التدقيق...' : auditRun ? 'إعادة التدقيق' : 'بدء التدقيق'}
        </button>
        {auditRun && (
          <button
            type="button"
            onClick={handleDownloadCsv}
            className="rounded-lg border-2 border-gray-300 bg-white px-6 py-2 font-bold text-gray-700 transition-colors hover:bg-gray-50"
          >
            تحميل التقرير (CSV)
          </button>
        )}
        {running && !progress && (
          <span className="text-sm text-gray-400">قد يستغرق التدقيق بضع دقائق...</span>
        )}
      </div>

      {/* SSE Progress bar (visible only when running) */}
      {running && (
        <div className="mb-4">
          <div className="mb-1 flex justify-between text-sm text-gray-500 font-tajawal">
            <span>جارٍ التدقيق...</span>
            <span>{toArabicDigits(progress)}٪</span>
          </div>
          <div className="h-2 w-full rounded-full bg-gray-200">
            <div
              className="h-2 rounded-full bg-mizan-navy transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {error && (
        <div className="mb-4 rounded-lg bg-red-50 p-4 text-center text-sm text-red-700">
          {error}
        </div>
      )}

      {results && overall && (
        <>
          {/* Overall metric cards (pinned above tabs — always visible) */}
          <div className="mb-4 grid grid-cols-4 gap-4">
            <div className="rounded-lg bg-white p-4 text-center shadow-sm">
              <p className="text-3xl font-bold text-mizan-navy">
                {toArabicDigits(Math.round(overall.f1 * 100))}٪
              </p>
              <p className="text-sm text-gray-500">F1 الإجمالي</p>
            </div>
            <div className="rounded-lg bg-white p-4 text-center shadow-sm">
              <p className="text-3xl font-bold text-blue-600">
                {toArabicDigits(Math.round(overall.precision * 100))}٪
              </p>
              <p className="text-sm text-gray-500">الدقة</p>
            </div>
            <div className="rounded-lg bg-white p-4 text-center shadow-sm">
              <p className="text-3xl font-bold text-blue-400">
                {toArabicDigits(Math.round(overall.recall * 100))}٪
              </p>
              <p className="text-sm text-gray-500">الاسترجاع</p>
            </div>
            <div className="rounded-lg bg-white p-4 text-center shadow-sm">
              <p className="text-3xl font-bold text-gray-600">
                {toArabicDigits(overall.total)}
              </p>
              <p className="text-sm text-gray-500">عدد الأمثلة</p>
            </div>
          </div>

          {/* Tab navigation */}
          <div className="mb-6 flex gap-1 border-b border-gray-200">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`border-b-2 px-4 pb-2 font-tajawal text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'border-mizan-navy text-mizan-navy'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab content */}
          <div>
            {activeTab === 'overview' && (
              <>
                {/* LLM-generated Arabic insight summary — Phase 10 streaming */}
                <div className="mb-6 rounded-lg border border-blue-200 bg-blue-50 p-4">
                  <h4 className="mb-2 text-sm font-bold text-blue-800">ملخص التحليل</h4>
                  {isInsightStreaming && !insightText ? (
                    <div className="flex items-center gap-2">
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
                      <span className="text-sm text-blue-500">جارٍ التحليل...</span>
                    </div>
                  ) : (
                    <p className="text-sm leading-relaxed text-blue-700">
                      {insightText ?? generateInsight(results)}
                      {isInsightStreaming && (
                        <span className="inline-block h-4 w-1 animate-pulse bg-blue-600 ms-1" />
                      )}
                    </p>
                  )}
                </div>

                {/* Weakness alert */}
                {weakCategories.length > 0 && (
                  <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4">
                    <p className="font-bold text-red-800">
                      فئات ضعيفة الأداء (F1 أقل من ٥٠٪):
                    </p>
                    <ul className="mt-2 list-inside list-disc text-sm text-red-700">
                      {weakCategories.map((c) => (
                        <li key={c.category}>
                          {c.category_ar} — F1: {toArabicDigits(Math.round(c.f1 * 100))}٪
                          ({toArabicDigits(c.sample_count)} عينة)
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Bias chart */}
                <div className="rounded-xl bg-white p-6 shadow-sm">
                  <h3 className="mb-4 text-lg font-bold text-mizan-navy">
                    أداء النموذج حسب الفئة
                  </h3>
                  <BiasChart data={perCategory} />
                </div>
              </>
            )}

            {activeTab === 'confidence' && (
              <div className="rounded-xl bg-white p-6 shadow-sm">
                <h3 className="mb-4 text-lg font-bold text-mizan-navy">
                  توزيع درجات الثقة حسب الفئة
                </h3>
                <ConfidenceHistogram
                  confidenceDist={results.confidence_dist ?? {}}
                  categoryLabels={CATEGORY_LABELS_AR}
                />
              </div>
            )}

            {activeTab === 'sources' && (
              <div className="rounded-xl bg-white p-6 shadow-sm">
                <h3 className="mb-4 text-lg font-bold text-mizan-navy">
                  أداء النموذج حسب مصدر البيانات
                </h3>
                <SourceBreakdownTable sources={results.per_source ?? []} />
              </div>
            )}

            {activeTab === 'falsepos' && (
              <div className="rounded-xl bg-white p-6 shadow-sm">
                <h3 className="mb-4 text-lg font-bold text-mizan-navy">
                  عينات الإيجابيات الكاذبة
                </h3>
                <p className="mb-4 text-sm text-gray-500">
                  أمثلة غير مؤذية صنّفها النموذج خطأً على أنها خطاب كراهية
                </p>
                <FalsePositiveList samples={results.false_positives ?? []} />
              </div>
            )}
          </div>

          {/* Audit metadata */}
          <div className="mt-4 text-center text-xs text-gray-400">
            آخر تدقيق: {new Date(auditRun.computed_at).toLocaleString('ar-JO')}
            {' · '}
            المدة: {toArabicDigits(Math.round(auditRun.duration_ms / 1000))} ثانية
          </div>
        </>
      )}

      {!results && !running && (
        <div className="rounded-xl bg-gray-50 p-12 text-center">
          <p className="text-lg text-gray-400">
            اضغط "بدء التدقيق" لتشغيل نموذج MARBERT على أمثلة قاعدة البيانات
          </p>
        </div>
      )}
    </div>
  )
}
