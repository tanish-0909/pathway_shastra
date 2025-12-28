import { clsx } from "clsx"
import type React from "react"

export interface PolicyData {
  bank: string
  rate: string
  bpsChange: number
  spreadVsFed: string
  sentiment: "Hawkish" | "Neutral" | "Dovish"
}

interface PolicyDifferentialDashboardProps {
  policyData: PolicyData[]
}

const getBpsChangeColor = (value: number) => {
  if (value > 0) return "text-emerald-300"
  if (value < 0) return "text-red-300"
  return "text-slate-300"
}

const getSpreadColor = (value: string) => {
  if (value.startsWith("-") && value !== "-0.00%") return "text-red-300"
  if (!value.startsWith("-") && value !== "0.00%") return "text-emerald-300"
  return "text-slate-200"
}

const getSentimentStyle = (sentiment: PolicyData["sentiment"]) => {
  switch (sentiment) {
    case "Hawkish":
      return "bg-red-950/60 text-red-300 border-red-900/60"
    case "Dovish":
      return "bg-emerald-950/70 text-emerald-300 border-emerald-900/60"
    case "Neutral":
      return "bg-slate-900/70 text-slate-300 border-slate-700/60"
  }
}

const getSentimentDotColor = (sentiment: PolicyData["sentiment"]) => {
  switch (sentiment) {
    case "Hawkish":
      return "bg-red-400"
    case "Dovish":
      return "bg-emerald-400"
    case "Neutral":
      return "bg-slate-400"
  }
}

export const PolicyDifferentialDashboard: React.FC<PolicyDifferentialDashboardProps> = ({
  policyData,
}) => {
  const hawkishCount = policyData.filter((p) => p.sentiment === "Hawkish").length
  const neutralCount = policyData.filter((p) => p.sentiment === "Neutral").length
  const dovishCount = policyData.filter((p) => p.sentiment === "Dovish").length

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#031615] via-[#071f1f] to-[#041818] px-4 py-8 text-sm text-gray-100">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-8">
        {/* Header */}
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
          <div>
            <h1 className="mb-1 text-3xl font-semibold tracking-tight text-white md:text-4xl">
              Policy Differential Dashboard
            </h1>
            <p className="text-sm text-gray-400">
              Cross–central bank rate levels, recent moves, and stance vs Fed.",
            </p>
          </div>

          {/* Quick sentiment stats */}
          <div className="flex flex-wrap gap-2 text-xs">
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-900/20 px-3 py-1">
              <span className="h-1.5 w-1.5 rounded-full bg-red-400" />
              <span className="font-medium text-emerald-200">Hawkish</span>
              <span className="text-emerald-100/80">{hawkishCount}</span>
            </div>
            <div className="inline-flex items-center gap-2 rounded-full border border-slate-500/30 bg-slate-900/40 px-3 py-1">
              <span className="h-1.5 w-1.5 rounded-full bg-slate-300" />
              <span className="font-medium text-slate-100">Neutral</span>
              <span className="text-slate-200/80">{neutralCount}</span>
            </div>
            <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-900/10 px-3 py-1">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-300" />
              <span className="font-medium text-emerald-100">Dovish</span>
              <span className="text-emerald-100/80">{dovishCount}</span>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-hidden rounded-2xl border border-emerald-900/40 bg-[#071a1a]/80 shadow-xl shadow-emerald-950/40 backdrop-blur">
          {/* Table Header */}
          <div className="grid grid-cols-[2fr,1fr,1fr,1fr,1fr] items-center gap-4 border-b border-emerald-900/40 bg-emerald-900/10 px-6 py-4 text-[11px] font-medium uppercase tracking-[0.16em] text-gray-400">
            <div>Bank</div>
            <div className="text-center">Rate</div>
            <div className="text-center">Δ bps vs prev</div>
            <div className="text-center">Spread vs Fed</div>
            <div className="text-right">Sentiment</div>
          </div>

          {/* Table Body */}
          <div className="divide-y divide-emerald-900/40">
            {policyData.map((row, index) => (
              <div
                key={row.bank}
                className={clsx(
                  "grid grid-cols-[2fr,1fr,1fr,1fr,1fr] items-center gap-4 px-6 py-5 text-sm transition-all",
                  "hover:bg-emerald-900/15 hover:shadow-[0_0_0_1px_rgba(16,185,129,0.15)]",
                  index % 2 === 0 && "bg-emerald-900/5"
                )}
              >
                {/* Bank */}
                <div className="text-base font-medium text-white">{row.bank}</div>

                {/* Rate */}
                <div className="text-center text-lg font-semibold tabular-nums text-emerald-100">
                  {row.rate}
                </div>

                {/* Δ BPS vs prev */}
                <div className="flex justify-center">
                  <span
                    className={clsx(
                      "inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm font-semibold tabular-nums",
                      row.bpsChange > 0 &&
                        "border-emerald-600/60 bg-emerald-950/50 text-emerald-300",
                      row.bpsChange < 0 &&
                        "border-red-600/60 bg-red-950/50 text-red-300",
                      row.bpsChange === 0 &&
                        "border-slate-600/50 bg-slate-900/60 text-slate-300"
                    )}
                  >
                    {row.bpsChange > 0 && "↑"}
                    {row.bpsChange < 0 && "↓"}
                    {row.bpsChange === 0 && "•"}
                    {Math.abs(row.bpsChange)} bps
                  </span>
                </div>

                {/* Spread vs Fed */}
                <div
                  className={clsx(
                    "text-center text-lg font-medium tabular-nums",
                    getSpreadColor(row.spreadVsFed)
                  )}
                >
                  {row.spreadVsFed}
                </div>

                {/* Sentiment */}
                <div className="flex justify-end">
                  <span
                    className={clsx(
                      "inline-flex items-center gap-2 rounded-full border px-3.5 py-1.5 text-xs font-medium tracking-wide",
                      getSentimentStyle(row.sentiment)
                    )}
                  >
                    <span
                      className={clsx(
                        "h-2 w-2 rounded-full",
                        getSentimentDotColor(row.sentiment)
                      )}
                    />
                    {row.sentiment}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer / meta */}
        <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] text-emerald-200/60">
          <span>Δ bps vs prev refers to the change from the last policy meeting.</span>
          <span className="font-mono">
            Snapshot view • All rates are policy / target rates.
          </span>
        </div>
      </div>
    </div>
  )
}

export default PolicyDifferentialDashboard
