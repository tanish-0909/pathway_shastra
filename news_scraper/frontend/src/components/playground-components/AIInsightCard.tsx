import type React from "react"

interface AIInsightCardProps {

  summary: string

  rationalePoints: string[]

  // Button
//   buttonLabel?: string
}

export const AIInsightCard: React.FC<AIInsightCardProps> = ({
  summary,
  rationalePoints,
//   buttonLabel = "Review Hedge Options",
}) => {
  return (
    <div className="w-full max-w-4xl rounded-3xl bg-gradient-to-br from-[#0d2d2f] to-[#0a1f21] p-12 shadow-2xl">
      {/* Header */}
      <h1 className="mb-8 text-5xl font-bold text-white">AI Insight</h1>

      {/* Summary Section */}
      <div className="mb-8">
        <h2 className="mb-4 text-xl font-medium text-gray-400">Summary</h2>
        <p className="text-2xl leading-relaxed text-white">
          {summary}
        </p>
      </div>

      {/* Rationale Section */}
      <div className="mb-8">
        <h2 className="mb-6 text-xl font-medium text-gray-400">Rationale</h2>
        <ul className="space-y-4">
          {rationalePoints.map((point, idx) => (
            <li key={idx} className="flex items-start gap-4">
              <span className="mt-2 h-2 w-2 flex-shrink-0 rounded-full bg-cyan-400"></span>
              <span className="text-xl text-gray-300">{point}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Divider */}
      <div className="mb-8 h-px bg-gray-700/50"></div>

      {/* Button */}
      <button className="rounded-full bg-[#0a2426] px-8 py-4 text-lg font-medium text-cyan-400 transition-all hover:bg-[#0d2d2f] hover:text-cyan-300">
        Review Hedge Options
      </button>
    </div>
  )
}
