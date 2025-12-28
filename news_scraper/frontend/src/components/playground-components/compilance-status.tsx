export interface ComplianceRule {
  ruleName: string
  actualPercent: number
  limitPercent: number
}

export interface ComplianceStatusProps {
  title?: string
  subtitle?: string
  rules: ComplianceRule[]
}

export function ComplianceStatusTable({
  title = "Compliance Status",
  subtitle = "Exposure vs Limits",
  rules,
}: ComplianceStatusProps) {
  const getBufferInfo = (actual: number, limit: number) => {
    const diff = limit - actual
    const isBreach = diff < 0
    return {
      value: Math.abs(diff).toFixed(1),
      isBreach,
      label: isBreach ? "Breach" : "Remaining",
    }
  }

  const getExposurePercentage = (actual: number, limit: number) => {
    // Cap at 100% for display purposes
    return Math.min((actual / limit) * 100, 100)
  }

  return (
    <div className="bg-[#0d2229] rounded-2xl p-6 w-full">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-white text-xl font-semibold">{title}</h2>
        <p className="text-gray-400 text-sm">{subtitle}</p>
      </div>

      {/* Table */}
      <div className="w-full">
        {/* Table Header */}
        <div className="grid grid-cols-[1.5fr_1fr_0.8fr_0.8fr_1fr] gap-4 pb-3 border-b border-gray-700/50">
          <span className="text-gray-400 text-xs uppercase tracking-wider">Rule Name</span>
          <span className="text-gray-400 text-xs uppercase tracking-wider">Exposure</span>
          <span className="text-gray-400 text-xs uppercase tracking-wider">Actual %</span>
          <span className="text-gray-400 text-xs uppercase tracking-wider">Limit %</span>
          <span className="text-gray-400 text-xs uppercase tracking-wider">Buffer</span>
        </div>

        {/* Table Body */}
        <div className="divide-y divide-gray-700/30">
          {rules.map((rule, index) => {
            const buffer = getBufferInfo(rule.actualPercent, rule.limitPercent)
            const exposureWidth = getExposurePercentage(rule.actualPercent, rule.limitPercent)

            return (
              <div key={index} className="grid grid-cols-[1.5fr_1fr_0.8fr_0.8fr_1fr] gap-4 py-4 items-center">
                {/* Rule Name */}
                <span className="text-white text-sm font-medium">{rule.ruleName}</span>

                {/* Exposure Bar */}
                <div className="w-full">
                  <div className="h-2.5 bg-gray-700/50 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-300 ${
                        buffer.isBreach ? "bg-[#e74c4c]" : "bg-[#2ecc71]"
                      }`}
                      style={{ width: `${exposureWidth}%` }}
                    />
                  </div>
                </div>

                {/* Actual % */}
                <span className={`text-sm ${buffer.isBreach ? "text-[#e74c4c]" : "text-white"}`}>
                  {rule.actualPercent.toFixed(1)}%
                </span>

                {/* Limit % */}
                <span className="text-white text-sm">{rule.limitPercent.toFixed(1)}%</span>

                {/* Buffer */}
                <span className={`text-sm ${buffer.isBreach ? "text-[#e74c4c]" : "text-gray-300"}`}>
                  {buffer.value}% {buffer.label}
                </span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
