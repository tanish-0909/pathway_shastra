import type React from "react"

interface CorrelationMatrixProps {
  labels: string[]
  matrix: number[][]

}

export const CorrelationMatrixFXCom: React.FC<CorrelationMatrixProps> = ({
  labels,
  matrix,
}) => {
  const getCellColor = (value: number): string => {
    if (value === 1.0) {
      return "bg-emerald-500"
    } else if (value >= 0.7) {
      return "bg-teal-500"
    } else if (value >= 0.4) {
      return "bg-teal-600"
    } else if (value >= 0) {
      return "bg-teal-700"
    } else if (value >= -0.5) {
      return "bg-red-900/80"
    } else {
      return "bg-red-900"
    }
  }

  return (
    <div className="w-full bg-gradient-to-br from-teal-950 via-slate-900 to-teal-950 rounded-3xl p-8 md:p-12">
      <div className="mb-8">
        <h1 className="text-white text-3xl md:text-4xl font-bold mb-2">
          
          Correlation (90D Rolling)
        </h1>
        <p className="text-gray-400 text-lg md:text-xl">
          FX pairs & Commodities Cross
        </p>
      </div>

      <div className="overflow-x-auto">
        <div className="inline-block min-w-full">
          {/* Header Row */}
          <div className="flex mb-2">
            <div className="w-32 md:w-40" />
            {labels.map((label, idx) => (
              <div
                key={`header-${idx}`}
                className="flex-1 min-w-[140px] md:min-w-[180px] text-center px-2"
              >
                <span className="text-gray-300 text-base md:text-lg font-medium">
                  {label}
                </span>
              </div>
            ))}
          </div>

          {/* Matrix Rows */}
          {matrix.map((row, rowIdx) => (
            <div key={`row-${rowIdx}`} className="flex mb-3">
              {/* Row Label */}
              <div className="w-32 md:w-40 flex items-center">
                <span className="text-gray-300 text-base md:text-lg font-medium">
                  {labels[rowIdx]}
                </span>
              </div>

              {/* Correlation Cells */}
              {row.map((value, colIdx) => (
                <div
                  key={`cell-${rowIdx}-${colIdx}`}
                  className="flex-1 min-w-[140px] md:min-w-[180px] px-2"
                >
                  <div
                    className={`${getCellColor(
                      value
                    )} rounded-xl py-4 md:py-5 flex items-center justify-center`}
                  >
                    <span className="text-white text-lg md:text-2xl font-semibold">
                      {value.toFixed(2)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
