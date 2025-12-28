"use client"

import type React from "react"

interface HeatmapCell {
  x: number
  y: number
  value: number | null
}

interface OptimizationHeatmapProps {
  xAxisLabel: string
  yAxisLabel: string
  gridCols: number
  gridRows: number
  heatmapData: HeatmapCell[]
}

export const OptimizationHeatmap: React.FC<OptimizationHeatmapProps> = ({
  xAxisLabel,
  yAxisLabel,
  gridCols,
  gridRows,
  heatmapData,
}) => {
  // Create a 2D array for easier rendering
  const grid: (number | null)[][] = Array(gridRows)
    .fill(null)
    .map(() => Array(gridCols).fill(null))

  heatmapData.forEach((cell) => {
    if (cell.y < gridRows && cell.x < gridCols) {
      grid[cell.y][cell.x] = cell.value
    }
  })

  const getColorClass = (cell: number | null): string => {
    if (cell === null) return "bg-[#134e4a]"
    if (cell >= 1.6) return "bg-[#2dd4bf]"
    if (cell >= 1.5) return "bg-[#14b8a6]"
    if (cell >= 1.4) return "bg-[#0d9488]"
    return "bg-[#0f766e]"
  }

  return (
    <div className="w-full h-full min-h-[600px] bg-[#0d2d2f] rounded-3xl p-8 text-white">
      {/* Header */}
      <div className="mb-12">
        <h2 className="text-2xl font-semibold mb-1">Optimization</h2>
        <p className="text-gray-400 text-sm">Parameter Tuning</p>
      </div>

      {/* Heatmap Container */}
      <div className="flex items-center justify-center h-[calc(100%-120px)]">
        <div className="flex gap-8 items-center w-full max-w-5xl">
          {/* Y-axis label */}
          <div className="flex-shrink-0">
            <p className="text-xs text-gray-400 -rotate-90 whitespace-nowrap origin-center">{yAxisLabel}</p>
          </div>

          {/* Grid Container */}
          <div className="flex-1 flex flex-col gap-2">
            {/* Grid */}
            <div className="grid gap-1" style={{ gridTemplateColumns: `repeat(${gridCols}, 1fr)` }}>
              {grid.map((row, rowIndex) =>
                row.map((cell, colIndex) => (
                  <div
                    key={`${rowIndex}-${colIndex}`}
                    className={`aspect-square flex items-center justify-center text-sm font-medium border-2 border-[#0d2d2f] ${getColorClass(cell)}`}
                  >
                    {cell !== null && cell}
                  </div>
                )),
              )}
            </div>

            {/* X-axis label */}
            <div className="mt-4 text-center">
              <p className="text-xs text-gray-400">{xAxisLabel}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}