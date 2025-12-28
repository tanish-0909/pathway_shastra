"use client"

import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

export interface ScenarioMetric {
  label: string
  currentValue: string
  scenarios: {
    ratesUp: {
      value: string
      change: string
      isPositive: boolean
    }
    recession: {
      value: string
      change: string
      isPositive: boolean
    }
  }
}

interface ScenarioComparisonProps {
  metrics: ScenarioMetric[]
  className?: string
}

export function ScenarioComparison({
  metrics,
  className,
}: ScenarioComparisonProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={cn("rounded-2xl bg-gradient-to-br from-teal-900 via-slate-900 to-slate-900 p-8", className)}
    >
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-white">Scenario Comparison</h2>
        <p className="mt-1 text-slate-400">Rate / FX / Bond Scenarios</p>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <div className="min-w-full">
          {/* Table Header */}
          <div className="grid grid-cols-4 gap-6 border-b border-slate-700 pb-4">
            <div className="text-left">
              <span className="text-sm font-medium text-slate-300">Metrics</span>
            </div>
            <div className="text-right">
              <span className="text-sm font-medium text-slate-300">Current/Base</span>
            </div>
            <div className="text-right">
              <span className="text-sm font-medium text-slate-300">Rates +50bps</span>
            </div>
            <div className="text-right">
              <span className="text-sm font-medium text-slate-300">Recession</span>
            </div>
          </div>

          {/* Table Body */}
          <div className="divide-y divide-slate-700/50">
            {metrics.map((metric, index) => (
              <motion.div
                key={metric.label}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
                className="grid grid-cols-4 gap-6 py-6"
              >
                {/* Metric Label */}
                <div className="flex items-center">
                  <span className="text-base font-medium text-white">{metric.label}</span>
                </div>

                {/* Current/Base Value */}
                <div className="flex items-center justify-end">
                  <span className="text-base font-medium text-slate-200">{metric.currentValue}</span>
                </div>

                {/* Rates +50bps Scenario */}
                <div className="flex flex-col items-end justify-center gap-1">
                  <span className="text-base font-medium text-white">
                    {metric.scenarios.ratesUp.value}
                  </span>
                  <span
                    className={cn(
                      "text-sm font-medium",
                      metric.scenarios.ratesUp.isPositive ? "text-emerald-400" : "text-red-400",
                    )}
                  >
                    ({metric.scenarios.ratesUp.change})
                  </span>
                </div>

                {/* Recession Scenario */}
                <div className="flex flex-col items-end justify-center gap-1">
                  <span className="text-base font-medium text-white">
                    {metric.scenarios.recession.value}
                  </span>
                  <span
                    className={cn(
                      "text-sm font-medium",
                      metric.scenarios.recession.isPositive ? "text-emerald-400" : "text-red-400",
                    )}
                  >
                    ({metric.scenarios.recession.change})
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  )
}
