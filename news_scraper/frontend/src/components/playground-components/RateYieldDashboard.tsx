"use client"

import { useState, useMemo } from "react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from "recharts"
import { motion } from "framer-motion"
import clsx from "clsx"
import type React from "react"

interface ChartDataPoint {
  date: string // ISO date format: "2020-01-01"
  policyRate: number
  yield10Y: number
}

interface MetricCard {
  label: string
  value: string
  change: string
  changeLabel: string
  changePositive: boolean
}

interface RateYieldDashboardProps {
  chartData: ChartDataPoint[]
  metricCards: MetricCard[]
}

type TimePeriod = "5Y" | "3Y" | "1Y" | "YTD"

export const RateYieldDashboard: React.FC<RateYieldDashboardProps> = ({ chartData, metricCards }) => {
  const [selectedPeriod, setSelectedPeriod] = useState<TimePeriod>("1Y")

  const filteredData = useMemo(() => {
    if (chartData.length === 0) return []

    const now = new Date()
    const currentYear = now.getFullYear()
    const startOfYear = new Date(currentYear, 0, 1)

    // Parse dates and sort data
    const sortedData = [...chartData].sort(
      (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
    )

    switch (selectedPeriod) {
      case "5Y": {
        const fiveYearsAgo = new Date(now)
        fiveYearsAgo.setFullYear(now.getFullYear() - 5)
        return sortedData.filter((d) => new Date(d.date) >= fiveYearsAgo)
      }
      case "3Y": {
        const threeYearsAgo = new Date(now)
        threeYearsAgo.setFullYear(now.getFullYear() - 3)
        return sortedData.filter((d) => new Date(d.date) >= threeYearsAgo)
      }
      case "1Y": {
        const oneYearAgo = new Date(now)
        oneYearAgo.setFullYear(now.getFullYear() - 1)
        return sortedData.filter((d) => new Date(d.date) >= oneYearAgo)
      }
      case "YTD": {
        return sortedData.filter((d) => new Date(d.date) >= startOfYear)
      }
      default:
        return sortedData
    }
  }, [chartData, selectedPeriod])

  // Format date for display on X-axis
  const formatXAxisDate = (dateString: string) => {
    const date = new Date(dateString)
    const year = date.getFullYear()
    const month = date.getMonth()
    
    // Show year labels at the start of each year
    if (month === 0) {
      return year.toString()
    }
    return ""
  }

  // Calculate Y-axis domain dynamically
  const yAxisDomain = useMemo(() => {
    if (filteredData.length === 0) return [0, 4]
    
    const allValues = filteredData.flatMap((d) => [d.policyRate, d.yield10Y])
    const minValue = Math.min(...allValues)
    const maxValue = Math.max(...allValues)
    
    // Add 10% padding
    const padding = (maxValue - minValue) * 0.1
    return [Math.max(0, Math.floor(minValue - padding)), Math.ceil(maxValue + padding)]
  }, [filteredData])

  return (
    <div className="w-full space-y-4 p-6">
      {/* Main Chart Card */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <div className="bg-[#0a2b2e] border-0 rounded-3xl p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold text-white">Rate vs Yield Overlay</h2>

            <div className="flex items-center gap-6">
              {/* Legend */}
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-0.5 border-t-2 border-dashed border-white" />
                  <span className="text-sm text-gray-400">Policy Rate</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-0.5 bg-cyan-400" />
                  <span className="text-sm text-white">10Y Yield</span>
                </div>
              </div>

              {/* Time Period Buttons */}
              <div className="flex items-center gap-2">
                {(["5Y", "3Y", "1Y", "YTD"] as TimePeriod[]).map((period) => (
                  <button
                    key={period}
                    onClick={() => setSelectedPeriod(period)}
                    className={clsx(
                      "px-4 py-1.5 rounded-full text-sm font-medium transition-all",
                      selectedPeriod === period ? "bg-cyan-500 text-white" : "text-gray-400 hover:text-white",
                    )}
                  >
                    {period}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Chart */}
          <div className="w-full h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={filteredData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="0" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis
                  dataKey="date"
                  stroke="#6b7280"
                  tick={{ fill: "#9ca3af", fontSize: 12 }}
                  axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
                  tickLine={false}
                  tickFormatter={formatXAxisDate}
                />
                <YAxis
                  stroke="#6b7280"
                  tick={{ fill: "#9ca3af", fontSize: 12 }}
                  axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
                  tickLine={false}
                  domain={yAxisDomain}
                  label={{
                    value: "Policy Rate (%)",
                    angle: -90,
                    position: "insideLeft",
                    fill: "#6b7280",
                    fontSize: 12,
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="policyRate"
                  stroke="white"
                  strokeWidth={2}
                  strokeDasharray="8 4"
                  dot={false}
                  animationDuration={1500}
                />
                <Line
                  type="monotone"
                  dataKey="yield10Y"
                  stroke="#06b6d4"
                  strokeWidth={3}
                  dot={false}
                  animationDuration={1500}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </motion.div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {metricCards.map((card, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 + index * 0.1 }}
          >
            <div className="bg-[#0a2b2e] border-0 rounded-3xl p-6">
              <div className="space-y-2">
                <p className="text-sm text-gray-400">{card.label}</p>
                <h3 className="text-4xl font-bold text-white">{card.value}</h3>
                <p className="text-sm">
                  <span className={`font-medium ${card.changePositive ? "text-emerald-500" : "text-red-500"}`}>
                    {card.change}
                  </span>
                  <span className="text-gray-400"> {card.changeLabel}</span>
                </p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}