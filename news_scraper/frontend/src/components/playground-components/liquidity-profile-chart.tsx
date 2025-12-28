export interface LiquidityDataPoint {
  id: string
  name: string
  spread: number
  depth: number
}

export interface LiquidityProfileChartProps {
  data: LiquidityDataPoint[]
  title?: string
  subtitle?: string
}

export function LiquidityProfileChart({
  data,
  title = "Liquidity Profile",
  subtitle = "Spread vs Depth",
}: LiquidityProfileChartProps) {
  // Calculate chart bounds with padding
  const maxSpread = Math.max(...data.map((d) => d.spread))
  const maxDepth = Math.max(...data.map((d) => d.depth))

  const chartWidth = 100
  const chartHeight = 100

  // Convert data point to chart position (percentage)
  const getPosition = (point: LiquidityDataPoint) => {
    const x = (point.spread / maxSpread) * 85 + 5 // 5-90% range
    const y = 100 - (point.depth / maxDepth) * 85 - 5 // Inverted Y, 5-90% range
    return { x, y }
  }

  // Generate horizontal grid lines
  const gridLines = [20, 40, 60, 80]

  return (
    <div className="bg-[#0d2125] rounded-xl p-6 w-full">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-white text-xl font-semibold">{title}</h2>
        <p className="text-gray-400 text-sm">{subtitle}</p>
      </div>

      {/* Chart Container */}
      <div className="relative">
        {/* High Liquidity Label */}
        <div className="absolute top-0 left-0 z-10">
          <span className="text-[#22c55e] text-xs font-medium tracking-wider">HIGH LIQUIDITY</span>
        </div>

        {/* Chart Area */}
        <div className="relative pt-8 pb-12 pl-8">
          {/* Y-Axis Label */}
          <div
            className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-2"
            style={{ writingMode: "vertical-rl", transform: "rotate(180deg) translateX(50%)" }}
          >
            <span className="text-gray-500 text-xs whitespace-nowrap">Depth (Market Volume/Liquidity Score)</span>
          </div>

          {/* Chart Grid and Points */}
          <div className="relative border-l border-b border-gray-700" style={{ height: "350px" }}>
            {/* Horizontal Grid Lines */}
            {gridLines.map((line) => (
              <div key={line} className="absolute w-full border-t border-gray-700/50" style={{ top: `${line}%` }} />
            ))}

            {/* Data Points */}
            {data.map((point) => {
              const pos = getPosition(point)
              return (
                <div
                  key={point.id}
                  className="absolute w-3 h-3 rounded-full bg-[#4fd1c5] border-2 border-[#81e6d9] shadow-[0_0_8px_rgba(79,209,197,0.5)] transform -translate-x-1/2 -translate-y-1/2 cursor-pointer hover:scale-125 transition-transform"
                  style={{
                    left: `${pos.x}%`,
                    top: `${pos.y}%`,
                  }}
                  title={`${point.name}: Spread ${point.spread}, Depth ${point.depth}`}
                />
              )
            })}

            {/* Low Liquidity Label */}
            <div className="absolute bottom-2 right-0">
              <span className="text-[#ef4444] text-xs font-medium tracking-wider">LOW LIQUIDITY</span>
            </div>
          </div>

          {/* X-Axis Label */}
          <div className="text-center mt-4">
            <span className="text-gray-500 text-sm">Spread (Bid-Ask Width)</span>
          </div>
        </div>
      </div>
    </div>
  )
}
