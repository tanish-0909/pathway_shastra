"use client"

import { useState } from "react"
import {
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  ReferenceLine,
} from "recharts"

type TimeFrame = "weekly" | "monthly" | "yearly"

interface CashFlowDataPoint {
  period: string
  inflow: number
  outflow: number
  netPosition: number
}

interface CashFlowForecastData {
  weekly: CashFlowDataPoint[]
  monthly: CashFlowDataPoint[]
  yearly: CashFlowDataPoint[]
}

interface CashFlowForecastChartProps {
  data: CashFlowForecastData
  title?: string
  subtitle?: string
}

export function CashFlowForecastChart({
  data,
  title = "Cash Flow Forecast",
  subtitle = "Projected Flows",
}: CashFlowForecastChartProps) {
  const [timeFrame, setTimeFrame] = useState<TimeFrame>("weekly")

  const currentData = data[timeFrame]

  const formatYAxis = (value: number) => {
    if (value === 0) return "0"
    const absValue = Math.abs(value)
    if (absValue >= 1000000) {
      return `${value / 1000000}M`
    }
    if (absValue >= 1000) {
      return `${value / 1000}K`
    }
    return value.toString()
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#0d2a2d] border border-[#1a5a5e] rounded-lg p-3 shadow-lg">
          <p className="text-white font-medium mb-2">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: ${Math.abs(entry.value / 1000000).toFixed(1)}M
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div className="bg-[#0d2a2d] rounded-2xl p-6 w-full">
      {/* Header */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-white text-xl font-semibold">{title}</h2>
          <p className="text-gray-400 text-sm">{subtitle}</p>
        </div>

        {/* Time Frame Toggle */}
        <div className="flex bg-[#0a1f21] rounded-lg overflow-hidden">
          {(["weekly", "monthly", "yearly"] as TimeFrame[]).map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeFrame(tf)}
              className={`px-4 py-2 text-sm font-medium transition-colors ${
                timeFrame === tf ? "bg-[#2a3a3d] text-white" : "text-gray-400 hover:text-white"
              }`}
            >
              {tf.charAt(0).toUpperCase() + tf.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Chart */}
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={currentData} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <defs>
              <linearGradient id="inflowGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#1a5a5e" stopOpacity={0.8} />
                <stop offset="100%" stopColor="#1a5a5e" stopOpacity={0.3} />
              </linearGradient>
              <linearGradient id="outflowGradient" x1="0" y1="1" x2="0" y2="0">
                <stop offset="0%" stopColor="#5c2626" stopOpacity={0.8} />
                <stop offset="100%" stopColor="#5c2626" stopOpacity={0.3} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1a3a3d" horizontal={true} vertical={false} />
            <XAxis
              dataKey="period"
              axisLine={{ stroke: "#1a3a3d" }}
              tickLine={false}
              tick={{ fill: "#9ca3af", fontSize: 12 }}
              dy={10}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#9ca3af", fontSize: 12 }}
              tickFormatter={formatYAxis}
              domain={[-12000000, 15000000]}
              ticks={[-10000000, -5000000, 0, 5000000, 10000000]}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine y={0} stroke="#3a4a4d" strokeWidth={1} />

            {/* Inflow Area (positive values) */}
            <Area
              type="monotone"
              dataKey="inflow"
              fill="url(#inflowGradient)"
              stroke="#1a5a5e"
              strokeWidth={0}
              name="Inflow"
            />

            {/* Outflow Area (negative values) */}
            <Area
              type="monotone"
              dataKey="outflow"
              fill="url(#outflowGradient)"
              stroke="#5c2626"
              strokeWidth={0}
              name="Outflow"
            />

            {/* Net Position Line */}
            <Line
              type="monotone"
              dataKey="netPosition"
              stroke="#ffffff"
              strokeWidth={3}
              dot={false}
              name="Net Position"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className="flex justify-center gap-6 mt-4">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-[#2dd4bf]" />
          <span className="text-gray-400 text-sm">Inflow</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-[#ef4444]" />
          <span className="text-gray-400 text-sm">Outflow</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5 bg-white" />
          <span className="text-gray-400 text-sm">Net Position</span>
        </div>
      </div>
    </div>
  )
}
