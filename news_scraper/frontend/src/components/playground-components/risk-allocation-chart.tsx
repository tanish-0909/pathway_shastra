"use client"

import type React from "react"

import { useEffect, useRef, useState, useCallback } from "react"

interface RiskAllocationItem {
  name: string
  percentage: number
  color: string
}

interface RiskAllocationData {
  allocations: RiskAllocationItem[]
}

interface RiskAllocationChartProps {
  data: RiskAllocationData
  title?: string
  subtitle?: string
  onSliceClick?: (item: RiskAllocationItem) => void
}

interface SliceGeometry {
  startAngle: number
  endAngle: number
  item: RiskAllocationItem
  index: number
}

export function RiskAllocationChart({
  data,
  title = "Risk Allocation",
  subtitle = "Risk Parity Contribution",
  onSliceClick,
}: RiskAllocationChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null)
  const sliceGeometryRef = useRef<SliceGeometry[]>([])
  const chartParamsRef = useRef<{ centerX: number; centerY: number; radius: number } | null>(null)

  const isPointInSlice = useCallback((x: number, y: number, slice: SliceGeometry): boolean => {
    if (!chartParamsRef.current) return false
    const { centerX, centerY, radius } = chartParamsRef.current

    const dx = x - centerX
    const dy = y - centerY
    const distance = Math.sqrt(dx * dx + dy * dy)

    if (distance > radius) return false

    let angle = Math.atan2(dy, dx)
    // Normalize angle to match our starting point (-PI/2)
    if (angle < -Math.PI / 2) {
      angle += Math.PI * 2
    }

    return angle >= slice.startAngle && angle < slice.endAngle
  }, [])

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLCanvasElement>) => {
      const canvas = canvasRef.current
      if (!canvas) return

      const rect = canvas.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top

      let foundIndex: number | null = null
      for (const slice of sliceGeometryRef.current) {
        if (isPointInSlice(x, y, slice)) {
          foundIndex = slice.index
          break
        }
      }

      setHoveredIndex(foundIndex)
      canvas.style.cursor = foundIndex !== null ? "pointer" : "default"
    },
    [isPointInSlice],
  )

  const handleClick = useCallback(
    (e: React.MouseEvent<HTMLCanvasElement>) => {
      const canvas = canvasRef.current
      if (!canvas) return

      const rect = canvas.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top

      for (const slice of sliceGeometryRef.current) {
        if (isPointInSlice(x, y, slice)) {
          setSelectedIndex((prev) => (prev === slice.index ? null : slice.index))
          onSliceClick?.(slice.item)
          break
        }
      }
    },
    [isPointInSlice, onSliceClick],
  )

  const handleLegendHover = useCallback((index: number | null) => {
    setHoveredIndex(index)
  }, [])

  const handleLegendClick = useCallback(
    (index: number, item: RiskAllocationItem) => {
      setSelectedIndex((prev) => (prev === index ? null : index))
      onSliceClick?.(item)
    },
    [onSliceClick],
  )

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Set canvas size for high DPI
    const dpr = window.devicePixelRatio || 1
    const rect = canvas.getBoundingClientRect()
    canvas.width = rect.width * dpr
    canvas.height = rect.height * dpr
    ctx.scale(dpr, dpr)

    const width = rect.width
    const height = rect.height
    const centerX = width * 0.65
    const centerY = height * 0.45
    const radius = Math.min(width, height) * 0.38

    chartParamsRef.current = { centerX, centerY, radius }

    // Clear canvas
    ctx.clearRect(0, 0, width, height)

    // Draw concentric circles (radar background)
    ctx.strokeStyle = "rgba(45, 90, 90, 0.3)"
    ctx.lineWidth = 1
    for (let i = 1; i <= 5; i++) {
      ctx.beginPath()
      ctx.arc(centerX, centerY, radius * (i / 5) * 1.3, 0, Math.PI * 2)
      ctx.stroke()
    }

    const sliceGeometry: SliceGeometry[] = []

    // Draw pie slices
    let startAngle = -Math.PI / 2
    const total = data.allocations.reduce((sum, item) => sum + item.percentage, 0)

    data.allocations.forEach((item, index) => {
      const sliceAngle = (item.percentage / total) * Math.PI * 2
      const endAngle = startAngle + sliceAngle

      sliceGeometry.push({ startAngle, endAngle, item, index })

      const isHovered = hoveredIndex === index
      const isSelected = selectedIndex === index
      const explosionOffset = isHovered || isSelected ? 8 : 0
      const midAngle = startAngle + sliceAngle / 2
      const offsetX = Math.cos(midAngle) * explosionOffset
      const offsetY = Math.sin(midAngle) * explosionOffset

      const scale = isHovered ? 1.02 : 1
      const sliceRadius = radius * scale

      // Draw slice with offset
      ctx.beginPath()
      ctx.moveTo(centerX + offsetX, centerY + offsetY)
      ctx.arc(centerX + offsetX, centerY + offsetY, sliceRadius, startAngle, endAngle)
      ctx.closePath()

      if (isHovered || isSelected) {
        ctx.fillStyle = brightenColor(item.color, isSelected ? 30 : 20)
        ctx.shadowColor = item.color
        ctx.shadowBlur = 15
      } else {
        ctx.fillStyle = item.color
        ctx.shadowBlur = 0
      }
      ctx.fill()

      // Draw slice border
      ctx.strokeStyle = isSelected ? "#ffffff" : "#0d2a2a"
      ctx.lineWidth = isSelected ? 3 : 2
      ctx.shadowBlur = 0
      ctx.stroke()

      // Calculate label position
      const labelRadius = radius * 1.15 + explosionOffset
      const labelX = centerX + Math.cos(midAngle) * labelRadius + offsetX
      const labelY = centerY + Math.sin(midAngle) * labelRadius + offsetY

      // Draw label background
      const labelText = `${item.name}: ${item.percentage}%`
      ctx.font = `${isHovered || isSelected ? "bold " : ""}12px system-ui, sans-serif`
      const textMetrics = ctx.measureText(labelText)
      const padding = 6
      const labelWidth = textMetrics.width + padding * 2
      const labelHeight = 22

      ctx.fillStyle = isHovered || isSelected ? "rgba(50, 80, 80, 0.95)" : "rgba(30, 50, 50, 0.9)"
      ctx.beginPath()
      ctx.roundRect(labelX - labelWidth / 2, labelY - labelHeight / 2, labelWidth, labelHeight, 4)
      ctx.fill()

      if (isHovered || isSelected) {
        ctx.strokeStyle = item.color
        ctx.lineWidth = 1.5
        ctx.stroke()
      }

      // Draw label text
      ctx.fillStyle = "#ffffff"
      ctx.textAlign = "center"
      ctx.textBaseline = "middle"
      ctx.fillText(labelText, labelX, labelY)

      startAngle = endAngle
    })

    sliceGeometryRef.current = sliceGeometry
  }, [data, hoveredIndex, selectedIndex])

  function brightenColor(color: string, amount: number): string {
    const hex = color.replace("#", "")
    const r = Math.min(255, Number.parseInt(hex.slice(0, 2), 16) + amount)
    const g = Math.min(255, Number.parseInt(hex.slice(2, 4), 16) + amount)
    const b = Math.min(255, Number.parseInt(hex.slice(4, 6), 16) + amount)
    return `rgb(${r}, ${g}, ${b})`
  }

  return (
    <div className="rounded-2xl p-6" style={{ backgroundColor: "#0d2a2a" }}>
      <div className="flex items-start justify-between">
        {/* Left side - Title and Legend */}
        <div className="flex-shrink-0">
          <h2 className="text-2xl font-bold text-white mb-1">{title}</h2>
          <p className="text-gray-400 text-sm mb-8">{subtitle}</p>

          <div className="space-y-5">
            {data.allocations.map((item, index) => (
              <div
                key={item.name}
                className={`flex items-center justify-between gap-16 cursor-pointer transition-all duration-200 rounded-lg px-2 py-1 -mx-2 ${
                  hoveredIndex === index || selectedIndex === index ? "bg-white/10" : "hover:bg-white/5"
                }`}
                onMouseEnter={() => handleLegendHover(index)}
                onMouseLeave={() => handleLegendHover(null)}
                onClick={() => handleLegendClick(index, item)}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-3 h-3 rounded-full transition-transform duration-200 ${
                      hoveredIndex === index || selectedIndex === index ? "scale-125" : ""
                    }`}
                    style={{ backgroundColor: item.color }}
                  />
                  <span
                    className={`text-white transition-all duration-200 ${
                      hoveredIndex === index || selectedIndex === index ? "font-medium" : ""
                    }`}
                  >
                    {item.name}
                  </span>
                </div>
                <span
                  className={`text-white transition-all duration-200 ${
                    hoveredIndex === index || selectedIndex === index ? "font-bold" : "font-medium"
                  }`}
                >
                  {item.percentage}%
                </span>
              </div>
            ))}
          </div>

          {selectedIndex !== null && (
            <div
              className="mt-6 p-4 rounded-lg border transition-all duration-300"
              style={{
                backgroundColor: "rgba(45, 90, 90, 0.3)",
                borderColor: data.allocations[selectedIndex].color,
              }}
            >
              <p className="text-gray-400 text-xs uppercase tracking-wide mb-1">Selected</p>
              <p className="text-white font-bold text-lg">{data.allocations[selectedIndex].name}</p>
              <p className="text-2xl font-bold" style={{ color: data.allocations[selectedIndex].color }}>
                {data.allocations[selectedIndex].percentage}%
              </p>
            </div>
          )}
        </div>

        {/* Right side - Chart */}
        <div className="flex-1 min-w-[300px]">
          <canvas
            ref={canvasRef}
            className="w-full h-[300px]"
            style={{ width: "100%", height: "300px" }}
            onMouseMove={handleMouseMove}
            onMouseLeave={() => setHoveredIndex(null)}
            onClick={handleClick}
          />
        </div>
      </div>
    </div>
  )
}
