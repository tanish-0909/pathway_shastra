"use client"

import type React from "react"
import { useState } from "react"

interface Asset {
  name: string
  price: string
  change?: number // allow undefined
  contribution?: number // allow undefined
}

interface TopMoversProps {
  gainers: Asset[]
  losers: Asset[]
}

export const TopMovers: React.FC<TopMoversProps> = ({
  gainers,
  losers,
}) => {
  const [activeTab, setActiveTab] = useState<"gainers" | "losers">("gainers")

  const assets = activeTab === "gainers" ? gainers : losers

  return (
    <div className="w-full h-full min-h-[600px] bg-[#0d2d2f] rounded-3xl p-8 text-white">
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <h2 className="text-3xl font-semibold mb-1">Top Movers</h2>
          <p className="text-gray-400 text-sm">Fixed Income & FX</p>
        </div>

        {/* Tab Toggle */}
        <div className="flex gap-2 bg-[#0f3a3d] rounded-lg p-1">
          <button
            onClick={() => setActiveTab("gainers")}
            className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === "gainers" ? "bg-[#0d9488] text-white" : "text-gray-400 hover:text-white"
            }`}
          >
            Gainers
          </button>
          <button
            onClick={() => setActiveTab("losers")}
            className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === "losers" ? "bg-[#0d9488] text-white" : "text-gray-400 hover:text-white"
            }`}
          >
            Losers
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="space-y-6">
        {/* Header Row */}
        <div className="grid grid-cols-12 gap-4 pb-4 border-b border-gray-700/50 text-sm text-gray-400 uppercase tracking-wider">
          <div className="col-span-3">Asset</div>
          <div className="col-span-2">Price</div>
          <div className="col-span-2">Δ%</div>
          <div className="col-span-5">Contribution</div>
        </div>

        {/* Data Rows */}
        {assets.map((asset, index) => {
          const change = typeof asset.change === 'number' ? asset.change : 0;
          const contribution = typeof asset.contribution === 'number' ? Math.max(0, Math.min(100, asset.contribution)) : 0;

          return (
            <div key={`${asset.name}-${index}`} className="grid grid-cols-12 gap-4 items-center py-4 border-b border-gray-700/30 last:border-0">
              <div className="col-span-3 text-base">{asset.name}</div>
              <div className="col-span-2 text-base">{asset.price}</div>
              <div className={`col-span-2 text-base font-medium ${change >= 0 ? "text-[#14b8a6]" : "text-[#ef4444]"}`}>
                {change >= 0 ? "+" : ""}
                {change.toFixed(2)}%
              </div>
              <div className="col-span-5">
                <div className="w-full h-2 bg-gray-800/50 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${change >= 0 ? "bg-[#14b8a6]" : "bg-[#ef4444]"}`}
                    style={{ width: `${contribution}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  )
}

export default TopMovers
