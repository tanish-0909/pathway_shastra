import { AlertTriangle } from "lucide-react"

export type RiskLevel = "low" | "medium" | "high"

export interface RiskCell {
  category: string
  level: RiskLevel
}

export interface RiskMapRow {
  sector: string
  risks: RiskCell[]
}

export interface RiskMapProps {
  data: RiskMapRow[]
  categories: string[]
  title?: string
  subtitle?: string
}

function getRiskColor(level: RiskLevel): string {
  switch (level) {
    case "high":
      return "bg-[#e05555]" // Red for high risk
    case "medium":
      return "bg-[#2a8a8a]" // Medium teal
    case "low":
    default:
      return "bg-[#1a6b6b]" // Teal for low risk
  }
}

export function RiskMap({ data, categories, title = "Risk Map", subtitle = "Sector x Risk Level" }: RiskMapProps) {
  return (
    <div className="bg-[#0d2626] rounded-2xl p-6 min-w-[800px]">
      {/* Header */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-white text-lg font-semibold">{title}</h2>
          <p className="text-[#6b9a9a] text-sm">{subtitle}</p>
        </div>
        <div className="flex gap-3">
          <button className="text-[#6b9a9a] hover:text-white transition-colors">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
            </svg>
          </button>
          <button className="text-[#6b9a9a] hover:text-white transition-colors">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
          </button>
          <button className="text-[#6b9a9a] hover:text-white transition-colors">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="1" />
              <circle cx="12" cy="5" r="1" />
              <circle cx="12" cy="19" r="1" />
            </svg>
          </button>
        </div>
      </div>

      {/* Grid */}
      <div className="overflow-x-auto">
        {/* Category Headers */}
        <div className="grid gap-2 mb-2" style={{ gridTemplateColumns: `100px repeat(${categories.length}, 1fr)` }}>
          <div /> {/* Empty cell for sector labels */}
          {categories.map((category) => (
            <div key={category} className="text-center text-[#8fb5b5] text-sm font-medium py-2">
              {category}
            </div>
          ))}
        </div>

        {/* Risk Rows */}
        {data.map((row) => (
          <div
            key={row.sector}
            className="grid gap-2 mb-2"
            style={{ gridTemplateColumns: `100px repeat(${categories.length}, 1fr)` }}
          >
            <div className="flex items-center text-[#8fb5b5] text-sm">{row.sector}</div>
            {row.risks.map((risk, index) => (
              <div
                key={`${row.sector}-${risk.category}-${index}`}
                className={`${getRiskColor(risk.level)} rounded-md h-10 flex items-center justify-center transition-all hover:opacity-80`}
              >
                {risk.level === "high" && <AlertTriangle className="w-5 h-5 text-white" />}
              </div>
            ))}
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="flex items-center justify-end mt-6 gap-2">
        <span className="text-[#6b9a9a] text-xs">Low</span>
        <div className="flex h-3 rounded overflow-hidden">
          <div className="w-8 bg-[#1a6b6b]" />
          <div className="w-8 bg-[#2a8a8a]" />
          <div className="w-8 bg-[#e05555]" />
        </div>
        <span className="text-[#6b9a9a] text-xs">High</span>
      </div>
    </div>
  )
}
