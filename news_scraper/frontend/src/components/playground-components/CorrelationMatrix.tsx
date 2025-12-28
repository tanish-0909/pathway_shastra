"use client"

import type React from "react"

interface CorrelationData {
  row: string
  col: string
  value: number
}

interface CorrelationMatrixProps {
  categories: string[]
  correlationData: CorrelationData[]
}

export const CorrelationMatrix: React.FC<CorrelationMatrixProps> = ({
  categories,
  correlationData,
}) => {
  const getColorClass = (value: number): string => {
    if (value === 1.0) return "bg-[#14b8a6]"
    if (value >= 0.7) return "bg-[#0d9488]"
    if (value >= 0.5) return "bg-[#0f766e]"
    if (value >= 0.2) return "bg-[#134e4a]"
    if (value >= 0) return "bg-[#1e3a3c]"
    if (value >= -0.2) return "bg-[#2d2d2d]"
    if (value >= -0.4) return "bg-[#5c2a2a]"
    if (value >= -0.7) return "bg-[#7f2828]"
    return "bg-[#b91c1c]"
  }

  const getValue = (row: string, col: string): number => {
    const data = correlationData.find((d) => d.row === row && d.col === col)
    return data ? data.value : 0
  }

  return (
    <div className="w-full bg-white p-6">
      {/* Correlation Pill */}
      <div className="mb-12">
        <span className="inline-block bg-[#a7f3d0] text-[#0d9488] px-6 py-2 rounded-full text-sm font-medium">
          Correlation
        </span>
      </div>

      {/* Matrix Container */}
      <div className="bg-[#0d2d2f] rounded-3xl p-8 text-white">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-1">Diversification</h2>
          <p className="text-gray-400 text-sm">Correlation Coefficients</p>
        </div>

        {/* Matrix Grid */}
        <div className="overflow-x-auto">
          <div className="inline-block min-w-full">
            {/* Column Headers */}
            <div className="grid gap-2 mb-2" style={{ gridTemplateColumns: `auto repeat(${categories.length}, 1fr)` }}>
              <div className=""></div>
              {categories.map((cat, index) => (
                <div key={index} className="text-center text-sm text-gray-400 px-4 py-2">
                  {cat}
                </div>
              ))}
            </div>

            {/* Matrix Rows */}
            {categories.map((rowCat, rowIndex) => (
              <div
                key={rowIndex}
                className="grid gap-2 mb-2"
                style={{ gridTemplateColumns: `auto repeat(${categories.length}, 1fr)` }}
              >
                {/* Row Label */}
                <div className="text-sm text-gray-400 flex items-center px-4">{rowCat}</div>

                {/* Cells */}
                {categories.map((colCat, colIndex) => {
                  const value = getValue(rowCat, colCat)
                  return (
                    <div
                      key={colIndex}
                      className={`${getColorClass(value)} rounded-xl px-6 py-6 flex items-center justify-center text-base font-medium`}
                    >
                      {value.toFixed(2)}
                    </div>
                  )
                })}
              </div>
            ))}
          </div>

          {/* Legend */}
          <div className="flex items-center justify-end gap-4 mt-8">
            <span className="text-xs text-gray-400">-1.0</span>
            <div className="flex gap-1">
              <div className="w-12 h-3 bg-[#b91c1c] rounded-sm"></div>
              <div className="w-12 h-3 bg-[#7f2828] rounded-sm"></div>
              <div className="w-12 h-3 bg-[#5c2a2a] rounded-sm"></div>
              <div className="w-12 h-3 bg-[#2d2d2d] rounded-sm"></div>
              <div className="w-12 h-3 bg-[#1e3a3c] rounded-sm"></div>
              <div className="w-12 h-3 bg-[#134e4a] rounded-sm"></div>
              <div className="w-12 h-3 bg-[#0f766e] rounded-sm"></div>
              <div className="w-12 h-3 bg-[#0d9488] rounded-sm"></div>
              <div className="w-12 h-3 bg-[#14b8a6] rounded-sm"></div>
            </div>
            <span className="text-xs text-gray-400">+1.0</span>
          </div>
        </div>
      </div>
    </div>
  )
}