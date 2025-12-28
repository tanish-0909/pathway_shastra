"use client"

import { cn } from "@/lib/utils"
import { useState } from "react"

export interface SectorData {
  name: string
  value: number
  isTotal?: boolean
}

interface AttributionBySectorProps {
  sectors: SectorData[]
  maxValue?: number  // optional axis max (default 4.0)
  minValue?: number  // optional axis min (default -4.0)
}

export function AttributionBySector({
  sectors,
  maxValue = 4.0,
  minValue = -4.0,
}: AttributionBySectorProps) {
  // Calculate positions and heights
  const range = maxValue - minValue

  const getBarStyle = (value: number, isTotal = false) => {
    const height = (Math.abs(value) / range) * 100
    const bottom = isTotal
      ? 50 // Total starts from 0 line
      : value > 0
        ? 50 // Positive values start from 0 line going up
        : 50 - (Math.abs(value) / range) * 100 // Negative values start below 0 line

    return {
      height: `${height}%`,
      bottom: `${bottom}%`,
    }
  }

  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)

  return (
    <div className="w-full h-full bg-[#0a1f1f] rounded-lg p-6 flex flex-col">
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-white text-2xl font-semibold mb-1">Attribution by Sector</h2>
        <p className="text-gray-400 text-sm">Sector/Region Contribution</p>
      </div>

      {/* Chart Container */}
      <div className="flex-1 relative flex items-end px-4">
        {/* Y-axis labels (fixed to match default range) */}
        <div className="absolute left-0 top-0 bottom-0 flex flex-col justify-between text-gray-400 text-xs pr-2">
          <span>{maxValue.toFixed(1)}%</span>
          <span>{(maxValue / 2).toFixed(1)}%</span>
          <span>0.0%</span>
          <span>{(minValue / 2).toFixed(1)}%</span>
          <span>{minValue.toFixed(1)}%</span>
        </div>

        {/* Grid lines */}
        <div className="absolute left-12 right-0 top-0 bottom-0">
          <div className="absolute left-0 right-0 top-0 border-t border-dashed border-gray-700" />
          <div className="absolute left-0 right-0 top-1/4 border-t border-dashed border-gray-700" />
          <div className="absolute left-0 right-0 top-1/2 border-t border-gray-600" />
          <div className="absolute left-0 right-0 top-3/4 border-t border-dashed border-gray-700" />
          <div className="absolute left-0 right-0 bottom-0 border-t border-dashed border-gray-700" />
        </div>

        {/* Bars Container */}
        <div className="flex-1 flex items-end justify-around relative ml-12 h-64">
          {sectors.map((sector, index) => {
            const barStyle = getBarStyle(sector.value, sector.isTotal)
            const isPositive = sector.value > 0
            const isNegative = sector.value < 0
            const isHovered = hoveredIndex === index

            return (
              <div key={`${sector.name}-${index}`} className="flex flex-col items-center flex-1 max-w-[140px]">
                {/* Bar */}
                <div
                  className="relative w-full flex justify-center mb-4 cursor-pointer"
                  style={{ height: "16rem" }}
                  onMouseEnter={() => setHoveredIndex(index)}
                  onMouseLeave={() => setHoveredIndex(null)}
                >
                  <div
                    className={cn(
                      "absolute w-3/4 transition-all duration-200 ease-out",
                      sector.isTotal
                        ? "bg-gray-500 hover:bg-gray-400"
                        : isPositive
                          ? "bg-emerald-400 hover:bg-emerald-300"
                          : isNegative
                            ? "bg-red-500 hover:bg-red-400"
                            : "bg-gray-500",
                      isHovered && "scale-110 shadow-lg",
                    )}
                    style={barStyle}
                  />

                  {isHovered && (
                    <div className="absolute -top-10 left-1/2 -translate-x-1/2 bg-gray-900 text-white px-3 py-1.5 rounded text-sm font-medium shadow-xl z-10 whitespace-nowrap animate-in fade-in slide-in-from-bottom-2 duration-200">
                      {sector.value > 0 ? "+" : ""}
                      {sector.value.toFixed(1)}%
                      <div className="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900" />
                    </div>
                  )}
                </div>

                {/* Label */}
                <span
                  className={cn(
                    "text-sm transition-all duration-200",
                    sector.isTotal ? "text-white font-semibold" : "text-gray-300",
                    isHovered && "text-white font-medium",
                  )}
                >
                  {sector.name}
                </span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
