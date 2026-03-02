import { useRef, useEffect } from 'react'
import * as d3 from 'd3'
import { toArabicDigits } from '../lib/format'

interface ConfidenceHistogramProps {
  confidenceDist: Record<string, { scores: number[]; count: number }>
  categoryLabels: Record<string, string>
}

const CHART_WIDTH = 140
const CHART_HEIGHT = 90
const MIN_SAMPLES = 20

export default function ConfidenceHistogram({
  confidenceDist,
  categoryLabels,
}: ConfidenceHistogramProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current) return

    const categories = Object.keys(categoryLabels)

    categories.forEach((cat) => {
      const svgContainer = containerRef.current!.querySelector(
        `[data-cat="${cat}"] .hist-svg-wrapper`
      )
      if (!svgContainer) return

      // Clear previous SVG
      d3.select(svgContainer).selectAll('*').remove()

      const scores = confidenceDist[cat]?.scores ?? []

      if (scores.length < MIN_SAMPLES) {
        // Insufficient data — show Arabic note (handled in JSX, skip SVG render)
        return
      }

      const margin = { top: 4, right: 4, bottom: 4, left: 4 }
      const innerWidth = CHART_WIDTH - margin.left - margin.right
      const innerHeight = CHART_HEIGHT - margin.top - margin.bottom

      const svg = d3
        .select(svgContainer)
        .append('svg')
        .attr('width', CHART_WIDTH)
        .attr('height', CHART_HEIGHT)
        .attr('viewBox', `0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`)

      const x = d3.scaleLinear().domain([0, 1]).range([0, innerWidth])

      const bins = d3
        .bin<number, number>()
        .value((d) => d)
        .domain([0, 1])
        .thresholds(10)(scores)

      const yMax = d3.max(bins, (b) => b.length) ?? 1
      const y = d3.scaleLinear().domain([0, yMax]).range([innerHeight, 0])

      svg
        .selectAll('rect')
        .data(bins)
        .enter()
        .append('rect')
        .attr('x', (b) => x(b.x0 ?? 0) + 1)
        .attr('y', (b) => y(b.length))
        .attr('width', (b) => Math.max(0, x(b.x1 ?? 0) - x(b.x0 ?? 0) - 1))
        .attr('height', (b) => innerHeight - y(b.length))
        .attr('fill', '#1e3a5f')
        .attr('rx', 1)
        .attr('opacity', 0.8)
    })
  }, [confidenceDist, categoryLabels])

  const categories = Object.keys(categoryLabels)

  return (
    <div>
      <div ref={containerRef} className="grid grid-cols-3 gap-4">
        {categories.map((cat) => {
          const scores = confidenceDist[cat]?.scores ?? []
          const hasEnoughData = scores.length >= MIN_SAMPLES

          return (
            <div key={cat} data-cat={cat} className="flex flex-col items-center">
              <p className="text-sm font-medium text-mizan-navy font-tajawal text-center mb-1">
                {categoryLabels[cat]}
              </p>
              {hasEnoughData ? (
                <div
                  className="hist-svg-wrapper w-full"
                  style={{ height: CHART_HEIGHT }}
                />
              ) : (
                <div
                  className="flex items-center justify-center rounded bg-gray-50 border border-dashed border-gray-200"
                  style={{ width: CHART_WIDTH, height: CHART_HEIGHT }}
                >
                  <p className="text-xs text-gray-400 font-tajawal text-center px-2 leading-relaxed">
                    {`عدد العينات غير كافٍ للتوزيع (${toArabicDigits(scores.length)})`}
                  </p>
                </div>
              )}
            </div>
          )
        })}
      </div>
      <p className="text-xs text-gray-400 font-tajawal text-center mt-3">
        {'٠٪ ← الثقة → ١٠٠٪'}
      </p>
    </div>
  )
}
