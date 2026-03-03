import { useRef, useEffect } from 'react'
import * as d3 from 'd3'
import type { CategoryMetrics } from '../lib/audit-api'

interface BiasChartProps {
  data: CategoryMetrics[]
}

export default function BiasChart({ data }: BiasChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current || data.length === 0) return

    d3.select(containerRef.current).selectAll('*').remove()

    // Filter to categories with samples
    const categories = data.filter((d) => d.sample_count > 0)
    if (categories.length === 0) return

    const margin = { top: 20, right: 120, bottom: 40, left: 120 }
    const barHeight = 28
    const groupGap = 12
    const height = categories.length * (barHeight * 3 + groupGap) + margin.top + margin.bottom
    const width = (containerRef.current.clientWidth || 600) - margin.left - margin.right

    const svg = d3
      .select(containerRef.current)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    // Scales
    const y = d3
      .scaleBand()
      .domain(categories.map((d) => d.category_ar))
      .range([0, height - margin.top - margin.bottom])
      .padding(0.2)

    const x = d3.scaleLinear().domain([0, 1]).range([0, width])

    const metrics = ['f1', 'precision', 'recall'] as const
    const metricLabels = { f1: 'F1', precision: 'دقة', recall: 'استرجاع' }
    const metricColors = { f1: '#1e3a5f', precision: '#3b82f6', recall: '#93c5fd' }

    // Y axis (Arabic category labels)
    svg
      .append('g')
      .call(d3.axisLeft(y))
      .selectAll('text')
      .attr('font-family', 'Tajawal, sans-serif')
      .attr('font-size', '13px')
      .attr('text-anchor', 'end')

    // X axis
    svg
      .append('g')
      .attr('transform', `translate(0,${height - margin.top - margin.bottom})`)
      .call(d3.axisBottom(x).ticks(5).tickFormat(d3.format('.0%')))
      .selectAll('text')
      .attr('font-size', '11px')

    // Grid lines
    svg
      .append('g')
      .attr('class', 'grid')
      .call(d3.axisBottom(x).ticks(5).tickSize(height - margin.top - margin.bottom).tickFormat(() => ''))
      .attr('opacity', 0.1)

    // Bars
    const bandwidth = y.bandwidth()
    const barSize = bandwidth / 3

    categories.forEach((cat) => {
      const yPos = y(cat.category_ar)!
      metrics.forEach((metric, idx) => {
        const value = cat[metric]

        // Color coding based on value (for F1 metric)
        let barColor = metricColors[metric]
        if (metric === 'f1') {
          if (value < 0.5) barColor = '#dc2626'
          else if (value < 0.7) barColor = '#f59e0b'
          else barColor = '#16a34a'
        }

        svg
          .append('rect')
          .attr('x', 0)
          .attr('y', yPos + idx * barSize)
          .attr('width', x(value))
          .attr('height', barSize - 2)
          .attr('fill', barColor)
          .attr('rx', 3)
          .attr('opacity', 0.85)

        // Value label
        svg
          .append('text')
          .attr('x', x(value) + 4)
          .attr('y', yPos + idx * barSize + barSize / 2)
          .attr('dy', '0.35em')
          .attr('font-family', 'Tajawal, sans-serif')
          .attr('font-size', '11px')
          .attr('fill', '#4b5563')
          .text(`${(value * 100).toFixed(0)}%`)
      })
    })

    // Legend
    const legend = svg
      .append('g')
      .attr('transform', `translate(${width + 10}, 0)`)

    metrics.forEach((metric, idx) => {
      legend
        .append('rect')
        .attr('x', 0)
        .attr('y', idx * 22)
        .attr('width', 14)
        .attr('height', 14)
        .attr('fill', metricColors[metric])
        .attr('rx', 2)

      legend
        .append('text')
        .attr('x', 20)
        .attr('y', idx * 22 + 11)
        .attr('font-family', 'Tajawal, sans-serif')
        .attr('font-size', '12px')
        .attr('fill', '#374151')
        .text(metricLabels[metric])
    })
  }, [data])

  return <div ref={containerRef} className="relative w-full" />
}
