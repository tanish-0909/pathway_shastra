"use client"

import type React from "react"
import { Search, SlidersHorizontal, Info } from "lucide-react"

interface Holding {
  ticker: string
  name: string
  quantity: number
  price: number
  plPercent: number
  weight: number
  var: string
  greeks: number
  liquidity: "High" | "Med" | "Low"
}

interface HoldingsDashboardProps {
  holdings: Holding[]
}

export const HoldingsDashboard: React.FC<HoldingsDashboardProps> = ({
  holdings,
}) => {
  const getLiquidityColor = (liquidity: string) => {
    switch (liquidity) {
      case "High":
        return "bg-emerald-500/20 text-emerald-400"
      case "Med":
        return "bg-yellow-500/20 text-yellow-400"
      case "Low":
        return "bg-red-500/20 text-red-400"
      default:
        return ""
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="mb-6">
        <h1 className="text-slate-400 text-lg">Treasury System Dashboard</h1>
      </div>

      <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-3xl p-8 shadow-2xl">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-white text-3xl font-bold">Holding</h2>

          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search by Ticker or Name..."
                className="bg-slate-800/50 border border-slate-700 rounded-xl pl-12 pr-4 py-3 text-slate-300 placeholder:text-slate-500 focus:outline-none focus:border-slate-600 w-80"
              />
            </div>
            <button className="bg-slate-800/50 border border-slate-700 rounded-xl p-3 hover:bg-slate-800 transition-colors">
              <SlidersHorizontal className="text-slate-400 w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700/50">
                <th className="text-left text-slate-400 text-xs font-semibold uppercase tracking-wider pb-4 px-4">
                  Ticker / Name
                </th>
                <th className="text-left text-slate-400 text-xs font-semibold uppercase tracking-wider pb-4 px-4">
                  QTY
                </th>
                <th className="text-left text-slate-400 text-xs font-semibold uppercase tracking-wider pb-4 px-4">
                  Price
                </th>
                <th className="text-left text-slate-400 text-xs font-semibold uppercase tracking-wider pb-4 px-4">
                  P/L %
                </th>
                <th className="text-left text-slate-400 text-xs font-semibold uppercase tracking-wider pb-4 px-4">
                  Weight %
                </th>
                <th className="text-left text-slate-400 text-xs font-semibold uppercase tracking-wider pb-4 px-4">
                  <div className="flex items-center gap-1">
                    VAR <Info className="w-3.5 h-3.5" />
                  </div>
                </th>
                <th className="text-left text-slate-400 text-xs font-semibold uppercase tracking-wider pb-4 px-4">
                  <div className="flex items-center gap-1">
                    Greeks <Info className="w-3.5 h-3.5" />
                  </div>
                </th>
                <th className="text-left text-slate-400 text-xs font-semibold uppercase tracking-wider pb-4 px-4">
                  <div className="flex items-center gap-1">
                    Liquidity <Info className="w-3.5 h-3.5" />
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              {holdings.map((holding) => (
                <tr
                  key={holding.ticker}
                  className="border-b border-slate-700/30 hover:bg-slate-800/30 transition-colors"
                >
                  <td className="py-6 px-4">
                    <div>
                      <div className="text-white font-semibold">{holding.ticker}</div>
                      <div className="text-slate-400 text-sm">{holding.name}</div>
                    </div>
                  </td>
                  <td className="py-6 px-4 text-slate-300">{holding.quantity}</td>
                  <td className="py-6 px-4 text-slate-300">${holding.price.toFixed(2)}</td>
                  <td className="py-6 px-4">
                    <span className={holding.plPercent >= 0 ? "text-emerald-400" : "text-red-400"}>
                      {holding.plPercent >= 0 ? "+" : ""}
                      {holding.plPercent.toFixed(2)}%
                    </span>
                  </td>
                  <td className="py-6 px-4">
                    <div className="flex items-center gap-3">
                      <div className="flex-1 bg-slate-700/30 rounded-full h-2 max-w-[120px]">
                        <div
                          className="bg-cyan-500 h-2 rounded-full"
                          style={{ width: `${(holding.weight / 20) * 100}%` }}
                        />
                      </div>
                      <span className="text-slate-300 text-sm min-w-[20px]">{holding.weight}</span>
                    </div>
                  </td>
                  <td className="py-6 px-4 text-slate-300">{holding.var}</td>
                  <td className="py-6 px-4 text-slate-300">Δ: {holding.greeks}</td>
                  <td className="py-6 px-4">
                    <span
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium ${getLiquidityColor(holding.liquidity)}`}
                    >
                      {holding.liquidity}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}