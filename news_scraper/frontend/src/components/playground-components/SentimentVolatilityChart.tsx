"use client"

import { motion } from "framer-motion"
import clsx from "clsx"
import { useState } from "react"

export interface DataPoint {
  ticker: string
  sentiment: number // -1.0 to +1.0
  volatility: number // 0 to 50+
}

interface SentimentVolatilityChartProps {
  className?: string
  data: DataPoint[]
}

export function SentimentVolatilityChart({
  className,
  data,
}: SentimentVolatilityChartProps) {
  // Chart dimensions
  const chartWidth = 560
  const chartHeight = 280
  const padding = { top: 20, right: 40, bottom: 40, left: 50 }
  const plotWidth = chartWidth - padding.left - padding.right
  const plotHeight = chartHeight - padding.top - padding.bottom

  // Axis ranges
  const xMin = -1.0
  const xMax = 1.0
  const yMin = 0
  const yMax = 50

  // Scale functions
  const scaleX = (value: number) => {
    return ((value - xMin) / (xMax - xMin)) * plotWidth + padding.left
  }

  const scaleY = (value: number) => {
    return chartHeight - padding.bottom - ((value - yMin) / (yMax - yMin)) * plotHeight
  }

  // Grid lines
  const xTicks = [-1.0, -0.5, 0, 0.5, 1.0]
  const yTicks = [0, 10, 20, 30, 40, 50]

  const [hoveredPoint, setHoveredPoint] = useState<string | null>(null)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className={clsx("rounded-2xl p-6 shadow-xl", className)}
      style={{ backgroundColor: "#0F2424" }}
    >
      {/* Header */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-white">Sentiment vs Volatility</h3>
        <p className="text-sm text-slate-400">Regime Forecast</p>
      </div>

      {/* Chart SVG */}
      <div className="relative">
        <svg width="100%" height="280" viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="overflow-visible">
          {/* Top-left quadrant (negative sentiment, high volatility) */}
          <rect
            x={padding.left}
            y={padding.top}
            width={plotWidth / 2}
            height={plotHeight / 2}
            fill="#0A1E1E"
            opacity="0.8"
          />

          {/* Top-right quadrant (positive sentiment, high volatility) */}
          <rect
            x={padding.left + plotWidth / 2}
            y={padding.top}
            width={plotWidth / 2}
            height={plotHeight / 2}
            fill="#142C2C"
            opacity="0.8"
          />

          {/* Bottom-left quadrant (negative sentiment, low volatility) */}
          <rect
            x={padding.left}
            y={padding.top + plotHeight / 2}
            width={plotWidth / 2}
            height={plotHeight / 2}
            fill="#0D2222"
            opacity="0.8"
          />

          {/* Bottom-right quadrant (positive sentiment, low volatility) */}
          <rect
            x={padding.left + plotWidth / 2}
            y={padding.top + plotHeight / 2}
            width={plotWidth / 2}
            height={plotHeight / 2}
            fill="#112828"
            opacity="0.8"
          />

          {/* Grid lines - Vertical */}
          {xTicks.map((tick, i) => (
            <line
              key={`v-grid-${i}`}
              x1={scaleX(tick)}
              y1={padding.top}
              x2={scaleX(tick)}
              y2={chartHeight - padding.bottom}
              stroke="rgba(148, 163, 184, 0.15)"
              strokeWidth="1"
            />
          ))}

          {/* Grid lines - Horizontal */}
          {yTicks.map((tick, i) => (
            <line
              key={`h-grid-${i}`}
              x1={padding.left}
              y1={scaleY(tick)}
              x2={chartWidth - padding.right}
              y2={scaleY(tick)}
              stroke="rgba(148, 163, 184, 0.15)"
              strokeWidth="1"
            />
          ))}

          {/* X-axis */}
          <line
            x1={padding.left}
            y1={chartHeight - padding.bottom}
            x2={chartWidth - padding.right}
            y2={chartHeight - padding.bottom}
            stroke="rgba(148, 163, 184, 0.3)"
            strokeWidth="2"
          />

          {/* Y-axis */}
          <line
            x1={padding.left}
            y1={padding.top}
            x2={padding.left}
            y2={chartHeight - padding.bottom}
            stroke="rgba(148, 163, 184, 0.3)"
            strokeWidth="2"
          />

          {/* X-axis labels */}
          {xTicks.map((tick, i) => (
            <text
              key={`x-label-${i}`}
              x={scaleX(tick)}
              y={chartHeight - padding.bottom + 20}
              textAnchor="middle"
              fill="rgba(148, 163, 184, 0.6)"
              fontSize="12"
              fontFamily="system-ui, -apple-system, sans-serif"
            >
              {tick > 0 ? `+${tick}` : tick}
            </text>
          ))}

          {/* Y-axis labels */}
          {yTicks.map((tick, i) => (
            <text
              key={`y-label-${i}`}
              x={padding.left - 10}
              y={scaleY(tick) + 4}
              textAnchor="end"
              fill="rgba(148, 163, 184, 0.6)"
              fontSize="12"
              fontFamily="system-ui, -apple-system, sans-serif"
            >
              {tick}
            </text>
          ))}

          {/* Axis titles */}
          <text
            x={chartWidth / 2}
            y={chartHeight - 5}
            textAnchor="middle"
            fill="rgba(148, 163, 184, 0.7)"
            fontSize="13"
            fontFamily="system-ui, -apple-system, sans-serif"
          >
            Sentiment Score
          </text>

          <text
            x={15}
            y={chartHeight / 2}
            textAnchor="middle"
            fill="rgba(148, 163, 184, 0.7)"
            fontSize="13"
            fontFamily="system-ui, -apple-system, sans-serif"
            transform={`rotate(-90, 15, ${chartHeight / 2})`}
          >
            IV Index
          </text>

          {/* Data points */}
          {data.map((point, i) => {
            const cx = scaleX(point.sentiment)
            const cy = scaleY(point.volatility)
            const isHovered = hoveredPoint === point.ticker

            return (
              <motion.g
                key={point.ticker}
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.1 * i + 0.2, duration: 0.3 }}
                onMouseEnter={() => setHoveredPoint(point.ticker)}
                onMouseLeave={() => setHoveredPoint(null)}
                className="cursor-pointer"
              >
                {isHovered && (
                  <motion.circle
                    cx={cx}
                    cy={cy}
                    r="16"
                    fill="rgba(255, 255, 255, 0.2)"
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0 }}
                    transition={{ duration: 0.2 }}
                  />
                )}

                <motion.circle
                  cx={cx}
                  cy={cy}
                  r="6"
                  fill="white"
                  animate={{
                    r: isHovered ? 8 : 6,
                    filter: isHovered ? "drop-shadow(0 0 8px rgba(255, 255, 255, 0.8))" : "none",
                  }}
                  transition={{ duration: 0.2 }}
                />

                <motion.text
                  x={cx + 12}
                  y={cy + 4}
                  fill="white"
                  fontSize="13"
                  fontFamily="system-ui, -apple-system, sans-serif"
                  className="pointer-events-none select-none"
                  animate={{
                    fontWeight: isHovered ? 700 : 500,
                    opacity: isHovered ? 1 : 0.9,
                  }}
                  transition={{ duration: 0.2 }}
                >
                  {point.ticker}
                </motion.text>

                {isHovered && (
                  <motion.g
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    {/* Tooltip background */}
                    <rect
                      x={cx - 60}
                      y={cy - 50}
                      width="120"
                      height="35"
                      rx="6"
                      fill="rgba(15, 36, 36, 0.95)"
                      stroke="rgba(255, 255, 255, 0.2)"
                      strokeWidth="1"
                    />
                    {/* Tooltip text */}
                    <text
                      x={cx}
                      y={cy - 35}
                      textAnchor="middle"
                      fill="white"
                      fontSize="11"
                      fontWeight="600"
                      fontFamily="system-ui, -apple-system, sans-serif"
                    >
                      {point.ticker}
                    </text>
                    <text
                      x={cx}
                      y={cy - 22}
                      textAnchor="middle"
                      fill="rgba(148, 163, 184, 0.9)"
                      fontSize="10"
                      fontFamily="system-ui, -apple-system, sans-serif"
                    >
                      Sentiment: {point.sentiment > 0 ? "+" : ""}
                      {point.sentiment.toFixed(2)} | IV: {point.volatility}
                    </text>
                  </motion.g>
                )}
              </motion.g>
            )
          })}
        </svg>
      </div>
    </motion.div>
  )
}
