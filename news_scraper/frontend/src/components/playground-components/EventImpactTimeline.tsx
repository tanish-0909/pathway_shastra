"use client"

import type React from "react"
import { ArrowDown, ArrowUp } from "lucide-react"
import { motion } from "framer-motion"
import { useState, useRef } from "react"

interface Event {
  name: string
  priceChange: number
  priceChangePercent: number
  volumeSpike: "High" | "Medium" | "Low"
  sentimentUp: boolean
  date: string
  price: number
}

interface EventImpactTimelineProps {
  dates: string[]
  prices: number[]
  events: Event[]
}

export const EventImpactTimeline: React.FC<EventImpactTimelineProps> = ({
  dates,
  prices,
  events,
}) => {
  const [hoveredPoint, setHoveredPoint] = useState<{ x: number; y: number; price: number; date: string } | null>(
    null,
  )
  const chartRef = useRef<HTMLDivElement>(null)

  const minPrice = Math.min(...prices)
  const maxPrice = Math.max(...prices)
  const priceRange = maxPrice - minPrice

  const getChartPosition = (index: number, price: number) => {
    const xPercent = (index / (dates.length - 1)) * 100
    const yPercent = ((maxPrice - price) / priceRange) * 80 + 10
    return { x: xPercent, y: yPercent }
  }

  const generatePath = () => {
    if (prices.length === 0) return ""

    let path = ""
    prices.forEach((price, index) => {
      const pos = getChartPosition(index, price)
      if (index === 0) {
        path += `M ${pos.x} ${pos.y}`
      } else {
        path += ` L ${pos.x} ${pos.y}`
      }
    })
    return path
  }

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!chartRef.current) return

    const rect = chartRef.current.getBoundingClientRect()
    const xPercent = ((e.clientX - rect.left) / rect.width) * 100
    const index = Math.round((xPercent / 100) * (dates.length - 1))
    const clampedIndex = Math.max(0, Math.min(dates.length - 1, index))

    const pos = getChartPosition(clampedIndex, prices[clampedIndex])
    setHoveredPoint({
      x: pos.x,
      y: pos.y,
      price: prices[clampedIndex],
      date: dates[clampedIndex],
    })
  }

  const handleMouseLeave = () => {
    setHoveredPoint(null)
  }

  const yAxisLabels = [
    maxPrice,
    maxPrice - priceRange * 0.25,
    maxPrice - priceRange * 0.5,
    maxPrice - priceRange * 0.75,
    minPrice,
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full rounded-3xl p-8 md:p-10"
      style={{ backgroundColor: "#0f2424" }}
    >
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-2xl md:text-3xl font-bold text-white mb-2"> Event Impact Timeline</h2>
        <p className="text-[#a8a8a8] text-sm md:text-base">Macro events vs asset moves</p>
      </div>

      {/* Chart Area */}
      <div className="relative mb-12 pl-12 pr-4">
        <div
          ref={chartRef}
          className="relative h-64 md:h-80"
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
        >
          {/* Y-axis labels */}
          <div className="absolute left-[-48px] top-0 bottom-0 flex flex-col justify-between text-xs text-[#a8a8a8]">
            {yAxisLabels.map((price, i) => (
              <div key={i} className="text-right">
                ${(price / 1000).toFixed(1)}k
              </div>
            ))}
          </div>

          {/* Background Grid Lines */}
          <div className="absolute inset-0">
            {[0, 1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="absolute w-full border-t"
                style={{
                  top: `${i * 25}%`,
                  borderColor: "rgba(255, 255, 255, 0.05)",
                }}
              />
            ))}
          </div>

          {/* SVG Chart */}
          <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
            <defs>
              <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#14b8b8" stopOpacity="0.6" />
                <stop offset="50%" stopColor="#14b8b8" stopOpacity="1" />
                <stop offset="100%" stopColor="#14b8b8" stopOpacity="0.8" />
              </linearGradient>
            </defs>
            <path 
              d={generatePath()} 
              fill="none" 
              stroke="url(#lineGradient)" 
              strokeWidth="0.4"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>

          {/* Event Markers */}
          {events.map((event, idx) => {
            const dateIndex = dates.indexOf(event.date)
            if (dateIndex === -1) return null
            
            const pos = getChartPosition(dateIndex, event.price)
            return (
              <motion.div
                key={event.name}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.3 + idx * 0.2, type: "spring" }}
                className="absolute z-10"
                style={{
                  left: `${pos.x}%`,
                  top: `${pos.y}%`,
                  transform: "translate(-50%, -50%)",
                }}
              >
                <div className="relative">
                  <div
                    className="w-5 h-5 rounded-full border-4 cursor-pointer hover:scale-110 transition-transform"
                    style={{
                      backgroundColor: event.sentimentUp ? "#14b8b8" : "#d63031",
                      borderColor: "#0f2424",
                    }}
                  />
                  <div
                    className="absolute inset-0 w-5 h-5 rounded-full animate-ping opacity-30"
                    style={{
                      backgroundColor: event.sentimentUp ? "#14b8b8" : "#d63031",
                    }}
                  />
                </div>
                <div className="absolute top-[-32px] left-1/2 -translate-x-1/2 whitespace-nowrap">
                  <span className="text-white text-xs md:text-sm font-medium">{event.name}</span>
                </div>
              </motion.div>
            )
          })}

          {/* Hover Tooltip */}
          {hoveredPoint && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              className="absolute z-20 pointer-events-none"
              style={{
                left: `${hoveredPoint.x}%`,
                top: `${hoveredPoint.y}%`,
                transform: "translate(-50%, -120%)",
              }}
            >
              <div className="bg-white/95 backdrop-blur-sm rounded-lg px-3 py-2 shadow-lg">
                <div className="text-xs font-semibold text-[#0f2424]">${hoveredPoint.price.toLocaleString()}</div>
                <div className="text-xs text-[#666]">{hoveredPoint.date}</div>
              </div>
              <div
                className="absolute left-1/2 -translate-x-1/2 w-0 h-0"
                style={{
                  borderLeft: "6px solid transparent",
                  borderRight: "6px solid transparent",
                  borderTop: "6px solid rgba(255, 255, 255, 0.95)",
                }}
              />
              <div
                className="absolute left-1/2 -translate-x-1/2 w-px bg-white/40"
                style={{ top: "100%", height: "20px" }}
              />
              <div
                className="absolute left-1/2 -translate-x-1/2 w-2 h-2 bg-white rounded-full border-2 border-[#14b8b8]"
                style={{ top: "calc(100% + 20px)" }}
              />
            </motion.div>
          )}

          {/* Timeline Labels */}
          <div className="absolute bottom-[-30px] w-full flex justify-between text-[#a8a8a8] text-xs md:text-sm">
            <span>{dates[0]}</span>
            <span>{dates[Math.floor(dates.length / 3)]}</span>
            <span>{dates[Math.floor(2 * dates.length / 3)]}</span>
            <span>{dates[dates.length - 1]}</span>
          </div>
        </div>
      </div>

      {/* Data Table */}
      <div className="mt-16">
        <div className="grid grid-cols-5 gap-4 mb-6 pb-4 border-b border-white/10">
          <div className="text-[#a8a8a8] text-sm font-medium">Event Name</div>
          <div className="text-[#a8a8a8] text-sm font-medium">Date</div>
          <div className="text-[#a8a8a8] text-sm font-medium">Price Δ</div>
          <div className="text-[#a8a8a8] text-sm font-medium">Volume Spike</div>
          <div className="text-[#a8a8a8] text-sm font-medium">Sentiment Shift</div>
        </div>

        {events.map((event, idx) => (
          <motion.div
            key={event.name}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 + idx * 0.1 }}
            className="grid grid-cols-5 gap-4 py-5 border-b border-white/5 hover:bg-white/5 transition-colors rounded-lg px-2 -mx-2"
          >
            <div className="text-white font-medium">{event.name}</div>
            <div className="text-[#a8a8a8]">{event.date}</div>
            <div
              className="font-medium"
              style={{
                color: event.priceChange >= 0 ? "#00b894" : "#d63031",
              }}
            >
              {event.priceChange >= 0 ? "+" : ""}${Math.abs(event.priceChange).toFixed(2)}{" "}
              <span className="text-sm">
                ({event.priceChangePercent >= 0 ? "+" : ""}
                {event.priceChangePercent.toFixed(1)}%)
              </span>
            </div>
            <div className="text-[#a8a8a8]">{event.volumeSpike}</div>
            <div>
              {event.sentimentUp ? (
                <ArrowUp className="text-[#00b894]" size={24} strokeWidth={2.5} />
              ) : (
                <ArrowDown className="text-[#d63031]" size={24} strokeWidth={2.5} />
              )}
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}