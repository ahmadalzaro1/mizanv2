import { useRef, useEffect } from 'react'
import * as d3 from 'd3'
import type { MonthlyData, HistoricalEvent } from '../lib/observatory-api'
import { toArabicDigits } from '../lib/format'

interface TimelineChartProps {
  data: MonthlyData[]
  events: HistoricalEvent[]
}

export default function TimelineChart({ data, events }: TimelineChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current || data.length === 0) return

    // Clear previous render
    d3.select(containerRef.current).selectAll('*').remove()

    const margin = { top: 30, right: 30, bottom: 60, left: 60 }
    const width = containerRef.current.clientWidth - margin.left - margin.right
    const height = 400 - margin.top - margin.bottom

    const svg = d3
      .select(containerRef.current)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    // Parse dates — use Date(year, month-1) for JS months (0-indexed)
    const parseDate = (d: MonthlyData) => new Date(d.year, d.month - 1)

    // Scales
    const x = d3
      .scaleTime()
      .domain(d3.extent(data, parseDate) as [Date, Date])
      .range([0, width])

    const maxHate = d3.max(data, (d) => d.hate_count) ?? 1
    const y = d3.scaleLinear().domain([0, maxHate * 1.1]).range([height, 0])

    // Area generator
    const area = d3
      .area<MonthlyData>()
      .x((d) => x(parseDate(d)))
      .y0(height)
      .y1((d) => y(d.hate_count))
      .curve(d3.curveMonotoneX)

    // Line generator
    const line = d3
      .line<MonthlyData>()
      .x((d) => x(parseDate(d)))
      .y((d) => y(d.hate_count))
      .curve(d3.curveMonotoneX)

    // Area fill
    svg
      .append('path')
      .datum(data)
      .attr('fill', 'rgba(220, 38, 38, 0.15)')
      .attr('d', area)

    // Line stroke
    svg
      .append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', '#dc2626')
      .attr('stroke-width', 2)
      .attr('d', line)

    // X axis
    svg
      .append('g')
      .attr('transform', `translate(0,${height})`)
      .call(
        d3.axisBottom(x).ticks(d3.timeYear.every(1)).tickFormat((d) => {
          const date = d as Date
          return toArabicDigits(date.getFullYear())
        })
      )
      .selectAll('text')
      .attr('font-family', 'Tajawal, sans-serif')
      .attr('font-size', '12px')

    // Y axis
    svg
      .append('g')
      .call(d3.axisLeft(y).ticks(5).tickFormat((d) => toArabicDigits(d as number)))
      .selectAll('text')
      .attr('font-family', 'Tajawal, sans-serif')
      .attr('font-size', '12px')

    // Event markers
    events.forEach((event) => {
      const eventDate = new Date(event.year, event.month - 1)
      const xPos = x(eventDate)

      // Vertical dashed line
      svg
        .append('line')
        .attr('x1', xPos)
        .attr('x2', xPos)
        .attr('y1', 0)
        .attr('y2', height)
        .attr('stroke', '#6b7280')
        .attr('stroke-width', 1)
        .attr('stroke-dasharray', '4,4')
        .attr('opacity', 0.6)

      // Event label (Arabic)
      svg
        .append('text')
        .attr('x', xPos)
        .attr('y', -8)
        .attr('text-anchor', 'middle')
        .attr('font-family', 'Tajawal, sans-serif')
        .attr('font-size', '10px')
        .attr('fill', '#4b5563')
        .text(event.label_ar)
    })

    // Tooltip
    const tooltip = d3
      .select(containerRef.current)
      .append('div')
      .style('position', 'absolute')
      .style('background', 'white')
      .style('border', '1px solid #e5e7eb')
      .style('border-radius', '8px')
      .style('padding', '8px 12px')
      .style('font-family', 'Tajawal, sans-serif')
      .style('font-size', '13px')
      .style('direction', 'rtl')
      .style('pointer-events', 'none')
      .style('opacity', 0)
      .style('box-shadow', '0 2px 8px rgba(0,0,0,0.1)')

    // Invisible overlay for hover
    svg
      .append('rect')
      .attr('width', width)
      .attr('height', height)
      .attr('fill', 'transparent')
      .on('mousemove', (mouseEvent) => {
        const [mx] = d3.pointer(mouseEvent)
        const hoveredDate = x.invert(mx)
        const bisector = d3.bisector<MonthlyData, Date>((d) => parseDate(d)).left
        const idx = bisector(data, hoveredDate, 1)
        const d0 = data[idx - 1]
        const d1 = data[idx]
        if (!d0) return
        const d = d1 && hoveredDate.getTime() - parseDate(d0).getTime() > parseDate(d1).getTime() - hoveredDate.getTime() ? d1 : d0

        tooltip
          .style('opacity', 1)
          .style('left', `${x(parseDate(d)) + margin.left + 10}px`)
          .style('top', `${y(d.hate_count) + margin.top - 10}px`)
          .html(
            `<strong>${toArabicDigits(d.year)}/${toArabicDigits(d.month)}</strong><br/>` +
            `خطاب كراهية: <strong>${toArabicDigits(d.hate_count)}</strong><br/>` +
            `إجمالي: ${toArabicDigits(d.total_count)}`
          )
      })
      .on('mouseout', () => tooltip.style('opacity', 0))
  }, [data, events])

  return (
    <div ref={containerRef} className="relative w-full" style={{ minHeight: 400 }} />
  )
}
