"use client"

interface LiquidityBufferData {
  currentPercent: number
  targetPercent: number
  maxPercent: number
}

interface LiquidityBufferGaugeProps {
  data: LiquidityBufferData
  title?: string
  subtitle?: string
}

export function LiquidityBufferGauge({
  data,
  title = "Liquidity Buffer",
  subtitle = "Buffer Adequacy",
}: LiquidityBufferGaugeProps) {
  const { currentPercent, targetPercent, maxPercent } = data

  // Calculate the position of the current value indicator (as percentage of bar width)
  const indicatorPosition = Math.min((currentPercent / maxPercent) * 100, 100)

  // Calculate target position
  const targetPosition = (targetPercent / maxPercent) * 100

  // Color segments as percentages of the bar
  // Red: 0-60%, Yellow: 60-80%, Light Teal: 80-100%, Bright Teal: 100-150%
  const segments = [
    { color: "#dc2626", width: 40 }, // Red (0-60% of target = 0-40% of 150)
    { color: "#eab308", width: 13.33 }, // Yellow (60-80% of target = 40-53.33% of 150)
    { color: "#2d8a8a", width: 13.33 }, // Light Teal (80-100% of target = 53.33-66.67% of 150)
    { color: "#2dd4bf", width: 33.34 }, // Bright Teal (100-150% = 66.67-100% of 150)
  ]

  return (
    <div className="rounded-2xl p-6 border border-[#2a4a4a]" style={{ backgroundColor: "#0d2a2a" }}>
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-white">{title}</h2>
        <p className="text-sm text-gray-400 mt-1">{subtitle}</p>
      </div>

      {/* Gauge Bar */}
      <div className="relative mb-2">
        {/* Background bar with segments */}
        <div className="h-4 rounded-full overflow-hidden flex">
          {segments.map((segment, index) => (
            <div
              key={index}
              className="h-full"
              style={{
                backgroundColor: segment.color,
                width: `${segment.width}%`,
              }}
            />
          ))}
        </div>

        {/* Current value indicator line */}
        <div
          className="absolute top-0 h-4 w-1 bg-white rounded-full shadow-lg"
          style={{
            left: `${indicatorPosition}%`,
            transform: "translateX(-50%)",
          }}
        />
      </div>

      {/* Labels below the bar */}
      <div className="relative flex justify-between text-sm text-gray-400 mb-8">
        <span>0%</span>
        <span
          className="absolute"
          style={{
            left: `${targetPosition}%`,
            transform: "translateX(-50%)",
          }}
        >
          Target
        </span>
        <span>{maxPercent}%</span>
      </div>

      {/* Current Value Display */}
      <div className="text-center">
        <p className="text-gray-400 text-lg">Current</p>
        <p className="text-6xl font-bold text-white my-2">{currentPercent}%</p>
        <p className="text-gray-400 text-lg">Target: {targetPercent}%</p>
      </div>
    </div>
  )
}
