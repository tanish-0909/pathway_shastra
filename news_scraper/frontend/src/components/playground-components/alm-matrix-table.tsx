"use client"

import { useMemo } from "react"

interface TimeBucket {
  period: string
  assets: number
  liabilities: number
}

interface ALMMatrixData {
  durationGapPercent: number
  timeBuckets: TimeBucket[]
}

interface ALMMatrixTableProps {
  data: ALMMatrixData
  title?: string
  subtitle?: string
}

function formatCurrency(value: number): string {
  const absValue = Math.abs(value)
  if (absValue >= 1000000000) {
    return `${value < 0 ? "-" : ""}$${(absValue / 1000000000).toFixed(0)}B`
  }
  if (absValue >= 1000000) {
    return `${value < 0 ? "-" : ""}$${(absValue / 1000000).toFixed(0)}M`
  }
  if (absValue >= 1000) {
    return `${value < 0 ? "-" : ""}$${(absValue / 1000).toFixed(0)}K`
  }
  return `${value < 0 ? "-" : ""}$${absValue}`
}

export function ALMMatrixTable({ data, title = "ALM Matrix", subtitle }: ALMMatrixTableProps) {
  const netGaps = useMemo(() => {
    return data.timeBuckets.map((bucket) => bucket.assets - bucket.liabilities)
  }, [data.timeBuckets])

  const displaySubtitle = subtitle || `Duration Gap %: ${data.durationGapPercent}%`

  return (
    <div className="rounded-2xl p-6" style={{ backgroundColor: "#0d2a2d" }}>
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-white">{title}</h2>
        <p className="text-sm text-gray-400">{displaySubtitle}</p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr style={{ backgroundColor: "#143a3d" }}>
              <th className="text-left py-3 px-4 text-xs font-medium text-gray-400 uppercase tracking-wider rounded-tl-lg w-48"></th>
              {data.timeBuckets.map((bucket, index) => (
                <th
                  key={bucket.period}
                  className={`text-center py-3 px-4 text-xs font-medium text-gray-400 uppercase tracking-wider ${
                    index === data.timeBuckets.length - 1 ? "rounded-tr-lg" : ""
                  }`}
                >
                  {bucket.period}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {/* Assets Row */}
            <tr className="border-b border-gray-700/30">
              <td className="py-4 px-4 text-sm text-gray-300">Assets</td>
              {data.timeBuckets.map((bucket) => (
                <td key={`assets-${bucket.period}`} className="py-4 px-4 text-center text-sm text-white">
                  {formatCurrency(bucket.assets)}
                </td>
              ))}
            </tr>

            {/* Liabilities Row */}
            <tr className="border-b border-gray-700/30">
              <td className="py-4 px-4 text-sm text-gray-300">Liabilities</td>
              {data.timeBuckets.map((bucket) => (
                <td key={`liabilities-${bucket.period}`} className="py-4 px-4 text-center text-sm text-white">
                  {formatCurrency(bucket.liabilities)}
                </td>
              ))}
            </tr>

            {/* Net Gap Row */}
            <tr>
              <td className="py-4 px-4 text-sm text-gray-300">Net Gap</td>
              {netGaps.map((gap, index) => (
                <td key={`gap-${data.timeBuckets[index].period}`} className="py-0 px-0">
                  <div
                    className="py-4 px-4 text-center text-sm font-medium text-white h-full"
                    style={{
                      backgroundColor: gap >= 0 ? "#1a5a5e" : "#5c2626",
                    }}
                  >
                    {formatCurrency(gap)}
                  </div>
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}
