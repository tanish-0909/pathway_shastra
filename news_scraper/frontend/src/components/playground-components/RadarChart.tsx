"use client"

import { useEffect, useRef } from "react"

interface RiskFactor {
  name: string
  exposure: number
  status: string
}

interface RadarChartProps {
  data: RiskFactor[]
}

export function RadarChart({ data }: RadarChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Set canvas size for high DPI displays
    const dpr = window.devicePixelRatio || 1
    const rect = canvas.getBoundingClientRect()
    canvas.width = rect.width * dpr
    canvas.height = rect.height * dpr
    ctx.scale(dpr, dpr)

    const centerX = rect.width / 2
    const centerY = rect.height / 2
    const maxRadius = Math.min(centerX, centerY) - 40
    const levels = 4
    const angleStep = (Math.PI * 2) / data.length

    // Clear canvas
    ctx.clearRect(0, 0, rect.width, rect.height)

    // Draw concentric circles and labels
    ctx.strokeStyle = "rgba(20, 184, 166, 0.2)"
    ctx.lineWidth = 1
    ctx.fillStyle = "rgba(156, 163, 175, 0.8)"
    ctx.font = "12px sans-serif"
    ctx.textAlign = "center"

    for (let i = 1; i <= levels; i++) {
      const radius = (maxRadius / levels) * i
      ctx.beginPath()
      ctx.arc(centerX, centerY, radius, 0, Math.PI * 2)
      ctx.stroke()

      // Draw percentage labels
      if (i === levels) {
        const label = "100%"
        ctx.fillText(label, centerX, centerY - radius - 10)
      } else if (i === 3) {
        const label = "75%"
        ctx.fillText(label, centerX, centerY - radius - 10)
      } else if (i === 2) {
        const label = "50%"
        ctx.fillText(label, centerX, centerY - radius - 10)
      } else if (i === 1) {
        const label = "25%"
        ctx.fillText(label, centerX, centerY - radius - 10)
      }
    }

    // Draw radial lines
    for (let i = 0; i < data.length; i++) {
      const angle = i * angleStep - Math.PI / 2
      const x = centerX + Math.cos(angle) * maxRadius
      const y = centerY + Math.sin(angle) * maxRadius

      ctx.beginPath()
      ctx.moveTo(centerX, centerY)
      ctx.lineTo(x, y)
      ctx.stroke()
    }

    // Calculate data points
    const points: { x: number; y: number }[] = []
    for (let i = 0; i < data.length; i++) {
      const angle = i * angleStep - Math.PI / 2
      const value = data[i].exposure / 100
      const radius = maxRadius * value
      const x = centerX + Math.cos(angle) * radius
      const y = centerY + Math.sin(angle) * radius
      points.push({ x, y })
    }

    // Draw filled polygon
    ctx.fillStyle = "rgba(34, 211, 238, 0.3)"
    ctx.strokeStyle = "rgba(34, 211, 238, 1)"
    ctx.lineWidth = 2
    ctx.beginPath()
    points.forEach((point, i) => {
      if (i === 0) {
        ctx.moveTo(point.x, point.y)
      } else {
        ctx.lineTo(point.x, point.y)
      }
    })
    ctx.closePath()
    ctx.fill()
    ctx.stroke()

    // Draw data points
    points.forEach((point) => {
      ctx.fillStyle = "rgba(34, 211, 238, 1)"
      ctx.beginPath()
      ctx.arc(point.x, point.y, 4, 0, Math.PI * 2)
      ctx.fill()
    })
  }, [data])

  return (
    <canvas ref={canvasRef} className="h-full w-full max-h-96 max-w-96" style={{ width: "400px", height: "400px" }} />
  )
}