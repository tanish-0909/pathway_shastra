interface CapitalHitScenario {
  name: string
  percentage: number
}

interface StressScenario {
  scenario: string
  lossPercent: number
  capitalHit: number
}

interface StressTestResultsData {
  capitalHitScenarios: CapitalHitScenario[]
  stressScenarios: StressScenario[]
}

interface StressTestResultsProps {
  data: StressTestResultsData
  title?: string
  subtitle?: string
}

export function StressTestResults({
  data,
  title = "Stress Test Results",
  subtitle = "Credit / FX / Rate Stress",
}: StressTestResultsProps) {
  const maxPercentage = Math.max(...data.capitalHitScenarios.map((s) => Math.abs(s.percentage)))

  const formatCurrency = (value: number) => {
    const absValue = Math.abs(value)
    if (absValue >= 1000000) {
      return `${value < 0 ? "-" : ""}$${absValue / 1000000}M`
    }
    return `${value < 0 ? "-" : ""}$${absValue}K`
  }

  return (
    <div className="bg-[#0d2a2b] rounded-2xl p-6 border border-[#1a4a4a]">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-white text-xl font-semibold">{title}</h2>
        <p className="text-gray-400 text-sm mt-1">{subtitle}</p>
      </div>

      {/* Capital Hit Bar Chart */}
      <div className="mb-8">
        <h3 className="text-white text-base font-medium mb-4">Capital Hit</h3>
        <div className="space-y-4">
          {data.capitalHitScenarios.map((scenario) => (
            <div key={scenario.name} className="flex items-center gap-4">
              <span className="text-gray-400 text-sm w-32 text-right">{scenario.name}</span>
              <div className="flex-1 flex items-center gap-3">
                {scenario.percentage === 0 ? (
                  <span className="text-gray-400 text-sm">0%</span>
                ) : (
                  <>
                    <div
                      className="h-4 bg-[#dc2626] rounded-full"
                      style={{
                        width: `${(Math.abs(scenario.percentage) / maxPercentage) * 100}%`,
                        maxWidth: "100%",
                      }}
                    />
                    <span className="text-[#dc2626] text-sm font-medium">{scenario.percentage}%</span>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Stress Scenarios Table */}
      <div className="bg-[#1a3a3a] rounded-lg overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-[#2a4a4a]">
              <th className="text-left py-4 px-6 text-gray-400 text-sm font-medium">Scenario</th>
              <th className="text-center py-4 px-6 text-gray-400 text-sm font-medium">Loss %</th>
              <th className="text-right py-4 px-6 text-gray-400 text-sm font-medium">Capital Hit</th>
            </tr>
          </thead>
          <tbody>
            {data.stressScenarios.map((scenario, index) => (
              <tr
                key={scenario.scenario}
                className={index < data.stressScenarios.length - 1 ? "border-b border-[#2a4a4a]" : ""}
              >
                <td className="py-5 px-6 text-white text-sm">{scenario.scenario}</td>
                <td className="py-5 px-6 text-center text-[#dc2626] text-sm font-medium">{scenario.lossPercent}%</td>
                <td className="py-5 px-6 text-right text-[#dc2626] text-sm font-medium">
                  {formatCurrency(scenario.capitalHit)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
