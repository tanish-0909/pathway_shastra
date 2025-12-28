interface AllocationItem {
  assetClass: string
  targetPercent: number
  actualPercent: number
}

interface AllocationVsPolicyTableProps {
  data: AllocationItem[]
  title?: string
  subtitle?: string
}

function getDeviationStyle(deviation: number): { bg: string; text: string } {
  const absDeviation = Math.abs(deviation)

  if (absDeviation >= 5) {
    return { bg: "bg-[#dc2626]", text: "text-white" } // Red for large drift
  } else if (absDeviation >= 3) {
    return { bg: "bg-[#d4a853]", text: "text-[#1a2a2a]" } // Yellow/amber for medium drift
  } else {
    return { bg: "bg-[#4a5a5a]", text: "text-white" } // Gray for small drift
  }
}

function formatDeviation(deviation: number): string {
  const sign = deviation > 0 ? "+" : ""
  return `${sign}${deviation}% Drift`
}

export function AllocationVsPolicyTable({
  data,
  title = "Allocation vs Policy",
  subtitle = "IPS Deviation",
}: AllocationVsPolicyTableProps) {
  return (
    <div className="bg-[#0d1f1f] rounded-2xl p-6 w-full">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-white text-xl font-semibold">{title}</h2>
        <p className="text-gray-400 text-sm">{subtitle}</p>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-[#2a3a3a]">
              <th className="text-left text-gray-400 text-xs uppercase tracking-wider py-3 font-medium">Asset Class</th>
              <th className="text-center text-gray-400 text-xs uppercase tracking-wider py-3 font-medium">Target %</th>
              <th className="text-center text-gray-400 text-xs uppercase tracking-wider py-3 font-medium">Actual %</th>
              <th className="text-center text-gray-400 text-xs uppercase tracking-wider py-3 font-medium">Deviation</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item, index) => {
              const deviation = item.actualPercent - item.targetPercent
              const { bg, text } = getDeviationStyle(deviation)

              return (
                <tr key={index} className="border-b border-[#1a2a2a] last:border-b-0">
                  <td className="py-5 text-white font-medium">{item.assetClass}</td>
                  <td className="py-5 text-gray-300 text-center">{item.targetPercent}%</td>
                  <td className="py-5 text-gray-300 text-center">{item.actualPercent}%</td>
                  <td className="py-5 text-center">
                    <span className={`inline-block px-4 py-1.5 rounded-full text-sm font-medium ${bg} ${text}`}>
                      {formatDeviation(deviation)}
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
