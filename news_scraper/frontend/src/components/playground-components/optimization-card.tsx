"use client"

import { ArrowDown, ArrowUp, Plus } from "lucide-react"

// Types
export type ActionType = "reduce" | "increase" | "allocate"

export interface Recommendation {
  id: string
  action: ActionType
  description: string
}

export interface OptimizationData {
  description: string
  recommendations: Recommendation[]
}

interface OptimizationCardProps {
  data: OptimizationData
  title?: string
  subtitle?: string
  onApply?: () => void
}

// Action icon component
function ActionIcon({ action }: { action: ActionType }) {
  switch (action) {
    case "reduce":
      return <ArrowDown className="w-5 h-5 text-red-500" />
    case "increase":
      return <ArrowUp className="w-5 h-5 text-green-500" />
    case "allocate":
      return <Plus className="w-5 h-5 text-teal-400" />
    default:
      return null
  }
}

export function OptimizationCard({
  data,
  title = "Optimization",
  subtitle = "Rebalance Suggestions",
  onApply,
}: OptimizationCardProps) {
  return (
    <div className="bg-[#0d2a2d] rounded-2xl p-8 border border-[#1a4a4a]">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white">{title}</h2>
        <p className="text-gray-400 text-sm mt-1">{subtitle}</p>
      </div>

      {/* Description */}
      <p className="text-gray-300 mb-6">{data.description}</p>

      {/* Recommendations List */}
      <div className="space-y-6 mb-8">
        {data.recommendations.map((rec) => (
          <div key={rec.id} className="flex items-start gap-4">
            <div className="mt-0.5">
              <ActionIcon action={rec.action} />
            </div>
            <p className="text-white">{rec.description}</p>
          </div>
        ))}
      </div>

      {/* Apply Button */}
      <div className="flex justify-end">
        <button
          onClick={onApply}
          className="bg-[#2dd4bf] hover:bg-[#14b8a6] text-[#0d2a2d] font-semibold px-8 py-3 rounded-full transition-colors"
        >
          Apply Actions
        </button>
      </div>
    </div>
  )
}
