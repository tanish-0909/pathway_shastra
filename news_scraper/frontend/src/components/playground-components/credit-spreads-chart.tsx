"use client"

import { LineChart, Line, XAxis, YAxis, ReferenceLine, ResponsiveContainer, CartesianGrid, Tooltip } from "recharts"

interface CreditSpreadDataPoint {
  month: string
  value: number
}

interface CreditSpreadsData {
  riskLimit: number
  chartData: CreditSpreadDataPoint[]
}

interface CreditSpreadsChartProps {
  data: CreditSpreadsData
  title?: string
  subtitle?: string
}

export function CreditSpreadsChart({
  data,
  title = "Credit Spreads",
  subtitle = "Spread Movements (bps)",
}: CreditSpreadsChartProps) {
  const { riskLimit, chartData } = data
  const latestValue = chartData[chartData.length - 1]?.value

  return (
    <div className="bg-[#0d2a2d] rounded-2xl p-6 w-full">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-white text-xl font-semibold">{title}</h2>
        <p className="text-gray-400 text-sm">{subtitle}</p>
      </div>

      {/* Chart */}
      <div className="h-80 relative">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 20, right: 80, left: 10, bottom: 20 }}>
            <CartesianGrid horizontal={true} vertical={false} stroke="#1a4a4f" strokeDasharray="0" />
            <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: "#9ca3af", fontSize: 12 }} dy={10} />
            <YAxis
              domain={[0, 250]}
              ticks={[0, 50, 100, 150, 200, 250]}
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#9ca3af", fontSize: 12 }}
              dx={-10}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="bg-[#2dd4bf] text-[#0d2a2d] px-3 py-1 rounded-full text-sm font-semibold">
                      {payload[0].value} bps
                    </div>
                  )
                }
                return null
              }}
            />
            {/* Risk Limit Reference Line */}
            <ReferenceLine
              y={riskLimit}
              stroke="#ef4444"
              strokeDasharray="8 4"
              strokeWidth={2}
              label={{
                value: "Risk Limit",
                position: "right",
                fill: "#ef4444",
                fontSize: 14,
                fontStyle: "italic",
              }}
            />
            {/* Main Line */}
            <Line
              type="monotone"
              dataKey="value"
              stroke="#2dd4bf"
              strokeWidth={2}
              dot={false}
              activeDot={{
                r: 6,
                fill: "#2dd4bf",
                stroke: "#0d2a2d",
                strokeWidth: 2,
              }}
            />
          </LineChart>
        </ResponsiveContainer>

        {/* Latest Value Label */}
        <div
          className="absolute bg-[#2dd4bf] text-[#0d2a2d] px-3 py-1 rounded-full text-sm font-semibold flex items-center gap-1"
          style={{ top: "28%", right: "8%" }}
        >
          <span className="italic">{latestValue} bps</span>
        </div>

        {/* Latest Value Dot */}
        <div
          className="absolute w-3 h-3 bg-[#2dd4bf] rounded-full border-2 border-[#0d2a2d]"
          style={{ top: "35%", right: "12%" }}
        />
      </div>
    </div>
  )
}
