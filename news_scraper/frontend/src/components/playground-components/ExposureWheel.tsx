"use client"

import { MoreVertical } from "lucide-react"
import { RadarChart } from "./RadarChart"
import type React from "react"

interface RiskFactor {
  name: string
  exposure: number
  status: string
}

interface ExposureWheelProps {
  riskData: RiskFactor[]
}

export const ExposureWheel: React.FC<ExposureWheelProps> = ({riskData }) => {
  const getStatusColor = (status: string): string => {
    const statusLower = status.toLowerCase()
    
    if (statusLower === "critical") return "text-red-500"
    if (statusLower === "very high") return "text-orange-500"
    if (statusLower === "high") return "text-yellow-500"
    if (statusLower === "medium") return "text-orange-400"
    if (statusLower === "low") return "text-green-500"
    
    return "text-gray-400"
  }

  return (
    <div className="w-full rounded-3xl bg-gradient-to-br from-teal-950 to-teal-900 p-8 text-white">
      {/* Header */}
      <div className="mb-12 flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Exposure Wheel</h2>
          <p className="text-gray-400">Risk Factor Breakdown</p>
        </div>
        <button className="text-gray-400 hover:text-white">
          <MoreVertical className="h-6 w-6" />
        </button>
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
        {/* Risk Factor Table */}
        <div className="space-y-6">
          {/* Table Header */}
          <div className="grid grid-cols-3 gap-4 border-b border-teal-800 pb-4">
            <div className="text-sm font-medium text-gray-300">Risk Factor</div>
            <div className="text-sm font-medium text-gray-300">Exposure %</div>
            <div className="text-sm font-medium text-gray-300">Status</div>
          </div>

          {/* Table Rows */}
          <div className="space-y-6">
            {riskData.map((risk, index) => (
              <div key={index} className="grid grid-cols-3 gap-4 border-b border-teal-800/50 pb-6 last:border-0">
                <div className="text-base">{risk.name}</div>
                <div className="text-base">{risk.exposure}%</div>
                <div className={`text-base font-medium ${getStatusColor(risk.status)}`}>{risk.status}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Radar Chart */}
        <div className="flex items-center justify-center">
          <RadarChart data={riskData} />
        </div>
      </div>
    </div>
  )
}