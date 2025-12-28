"use client"

import { useMemo } from "react"
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell } from "recharts"

interface CapitalEfficiencyItem {
  category: string
  rwa: number
  capital: number
}
  
interface CapitalEfficiencyChartProps {
  data: CapitalEfficiencyItem[]
  title?: string
  subtitle?: string
}

export function CapitalEfficiencyChart({
  data,
  title = "Capital Efficiency",
  subtitle = "RWA vs Capital",
}: CapitalEfficiencyChartProps) {
  const chartData = useMemo(() => {
    return data.map((item) => ({
      ...item,
      categoryLabel: item.category,
    }))
  }, [data])

  const formatYAxis = (value: number) => {
    if (value === 0) return "$0M"
    return `$${value}M`
  }

  const maxValue = useMemo(() => {
    const max = Math.max(...data.map((d) => Math.max(d.rwa, d.capital)))
    return Math.ceil(max / 50) * 50
  }, [data])

  return (
    <div className="w-full rounded-2xl p-6" style={{ backgroundColor: "#0d2a2d" }}>
      {/* Header */}
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white">{title}</h2>
          <p className="text-sm text-gray-400">{subtitle}</p>
        </div>
        {/* Legend */}
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="h-4 w-4 rounded-sm" style={{ backgroundColor: "#2dd4bf" }} />
            <span className="text-sm text-gray-300">RWA</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-4 w-4 rounded-sm border-2 border-white" style={{ backgroundColor: "transparent" }} />
            <span className="text-sm text-gray-300">Capital</span>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
            barCategoryGap="20%"
            barGap={8}
          >
            <XAxis
              dataKey="categoryLabel"
              axisLine={{ stroke: "#374151" }}
              tickLine={false}
              tick={{ fill: "#9ca3af", fontSize: 12 }}
              dy={10}
            />
            <YAxis
              axisLine={{ stroke: "#374151" }}
              tickLine={false}
              tick={{ fill: "#9ca3af", fontSize: 12 }}
              tickFormatter={formatYAxis}
              domain={[0, maxValue]}
              ticks={[0, 50, 100, 150]}
            />
            {/* Horizontal grid lines */}
            <defs>
              <pattern id="gridPattern" width="100%" height="50" patternUnits="userSpaceOnUse">
                <line x1="0" y1="0" x2="100%" y2="0" stroke="#374151" strokeWidth="1" strokeDasharray="4 4" />
              </pattern>
            </defs>
            {/* RWA Bars - Solid Teal */}
            <Bar dataKey="rwa" fill="#2dd4bf" radius={[2, 2, 0, 0]} barSize={60}>
              {chartData.map((entry, index) => (
                <Cell key={`rwa-${index}`} fill="#2dd4bf" />
              ))}
            </Bar>
            {/* Capital Bars - Outlined */}
            <Bar
              dataKey="capital"
              fill="transparent"
              stroke="#ffffff"
              strokeWidth={2}
              radius={[2, 2, 0, 0]}
              barSize={60}
            >
              {chartData.map((entry, index) => (
                <Cell key={`capital-${index}`} fill="transparent" stroke="#ffffff" strokeWidth={2} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
