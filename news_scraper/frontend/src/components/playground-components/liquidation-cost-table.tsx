import { Filter, Download, MoreVertical } from "lucide-react"

export interface LiquidationCostItem {
  component: string
  spreadCost: number
  impactCost: number
  totalEstCost: number
  isTotal?: boolean
}

export interface LiquidationCostData {
  items: LiquidationCostItem[]
}

interface LiquidationCostTableProps {
  data: LiquidationCostData
  title?: string
  subtitle?: string
  showActions?: boolean
}

export function LiquidationCostTable({
  data,
  title = "Liquidation Cost",
  subtitle = "Estimated Transaction Impact",
  showActions = true,
}: LiquidationCostTableProps) {
  const formatCurrency = (value: number) => {
    return `$${value.toLocaleString()}`
  }

  const formatBps = (value: number) => {
    return `${value} bps`
  }

  return (
    <div className="bg-[#0d2528] rounded-2xl p-6 min-w-[500px]">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-white text-xl font-semibold">{title}</h2>
          <p className="text-slate-400 text-sm">{subtitle}</p>
        </div>
        {showActions && (
          <div className="flex items-center gap-3">
            <button className="text-slate-400 hover:text-white transition-colors">
              <Filter size={18} />
            </button>
            <button className="text-slate-400 hover:text-white transition-colors">
              <Download size={18} />
            </button>
            <button className="text-slate-400 hover:text-white transition-colors">
              <MoreVertical size={18} />
            </button>
          </div>
        )}
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700/50">
              <th className="text-left text-slate-400 text-xs font-medium uppercase tracking-wider py-3 pr-4">
                Component
              </th>
              <th className="text-left text-slate-400 text-xs font-medium uppercase tracking-wider py-3 px-4">
                Spread Cost
              </th>
              <th className="text-left text-slate-400 text-xs font-medium uppercase tracking-wider py-3 px-4">
                Impact Cost
              </th>
              <th className="text-left text-slate-400 text-xs font-medium uppercase tracking-wider py-3 pl-4">
                Total Est. Cost
              </th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((item, index) => (
              <tr
                key={index}
                className={`border-b border-slate-700/30 last:border-b-0 ${item.isTotal ? "bg-[#0f2d30]" : ""}`}
              >
                <td className={`py-4 pr-4 ${item.isTotal ? "text-white font-semibold" : "text-slate-300"}`}>
                  {item.component}
                </td>
                <td className="py-4 px-4 text-slate-300">{formatBps(item.spreadCost)}</td>
                <td className="py-4 px-4 text-slate-300">{formatBps(item.impactCost)}</td>
                <td className="py-4 pl-4 text-[#ef4444] font-medium">{formatCurrency(item.totalEstCost)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
