"use client"

import { useState } from "react"

interface AssetAllocation {
  name: string
  oldPercent: number
  newPercent: number
}

export default function RebalanceSimulation() {
  const [allocations, setAllocations] = useState<AssetAllocation[]>([
    { name: "Global Equities", oldPercent: 40, newPercent: 45 },
    { name: "Fixed Income", oldPercent: 30, newPercent: 25 },
    { name: "Real Estate", oldPercent: 15, newPercent: 15 },
    { name: "Commodities", oldPercent: 15, newPercent: 15 },
  ])

  const handleSliderChange = (index: number, value: number) => {
    const newAllocations = [...allocations]
    newAllocations[index].newPercent = value
    setAllocations(newAllocations)
  }

  const calculateDelta = (oldVal: number, newVal: number) => {
    const delta = newVal - oldVal
    if (delta > 0) return `+${delta}%`
    if (delta < 0) return `${delta}%`
    return "0%"
  }

  const getDeltaColor = (oldVal: number, newVal: number) => {
    const delta = newVal - oldVal
    if (delta > 0) return "text-teal-400"
    if (delta < 0) return "text-red-500"
    return "text-gray-400"
  }

  const total = allocations.reduce((sum, item) => sum + item.newPercent, 0)

  const handleReset = () => {
    setAllocations([
      { name: "Global Equities", oldPercent: 40, newPercent: 40 },
      { name: "Fixed Income", oldPercent: 30, newPercent: 30 },
      { name: "Real Estate", oldPercent: 15, newPercent: 15 },
      { name: "Commodities", oldPercent: 15, newPercent: 15 },
    ])
  }

  return (
    <div className="w-full max-w-7xl mx-auto bg-[#0f2e2e] rounded-3xl p-10 shadow-2xl">
      
      {/* Header */}
      <div className="flex items-center justify-between mb-8 pb-6 border-b border-gray-700/50">
        <h1 className="text-white text-4xl font-bold">Rebalance Simulation</h1>
        <button onClick={handleReset} className="text-gray-400 hover:text-white text-lg transition-colors">
          Reset
        </button>
      </div>

      {/* Table Header */}
      <div className="grid grid-cols-[2fr,4fr,1fr,1fr,1fr] gap-6 mb-8 px-4">
        <div className="text-gray-400 text-lg">Asset Class</div>
        <div className="text-gray-400 text-lg">Allocation</div>
        <div className="text-gray-400 text-lg text-right">Old %</div>
        <div className="text-gray-400 text-lg text-right">New %</div>
        <div className="text-gray-400 text-lg text-right">Δ%</div>
      </div>

      {/* Asset Rows */}
      <div className="space-y-8 mb-12">
        {allocations.map((asset, index) => (
          <div key={index} className="grid grid-cols-[2fr,4fr,1fr,1fr,1fr] gap-6 items-center px-4">
            <div className="text-white text-xl">{asset.name}</div>

            <div className="relative">
              <input
                type="range"
                min="0"
                max="100"
                value={asset.newPercent}
                onChange={(e) => handleSliderChange(index, Number(e.target.value))}
                className="w-full h-2 bg-transparent appearance-none cursor-pointer slider-track"
                style={{
                  background: `linear-gradient(to right, #14b8a6 0%, #14b8a6 ${asset.newPercent}%, #1e4d4d ${asset.newPercent}%, #1e4d4d 100%)`,
                }}
              />
            </div>

            <div className="text-gray-400 text-xl text-right">{asset.oldPercent}%</div>
            <div className="text-white text-xl font-bold text-right">{asset.newPercent}%</div>
            <div className={`text-xl font-bold text-right ${getDeltaColor(asset.oldPercent, asset.newPercent)}`}>
              {calculateDelta(asset.oldPercent, asset.newPercent)}
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-8 border-t border-gray-700/50">
        <div className="text-white text-2xl font-bold">Total: {total}%</div>
        <button className="bg-teal-600 hover:bg-teal-700 text-white text-xl font-semibold px-12 py-4 rounded-xl transition-colors">
          Execute Rebalance
        </button>
      </div>

      {/* FIXED – Normal style tag (not styled-jsx) */}
      <style>{`
        input[type='range']::-webkit-slider-thumb {
          appearance: none;
          width: 24px;
          height: 24px;
          border-radius: 50%;
          background: white;
          cursor: pointer;
          border: 2px solid #0f2e2e;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        input[type='range']::-moz-range-thumb {
          width: 24px;
          height: 24px;
          border-radius: 50%;
          background: white;
          cursor: pointer;
          border: 2px solid #0f2e2e;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        input[type='range']::-webkit-slider-runnable-track {
          height: 8px;
          border-radius: 4px;
        }

        input[type='range']::-moz-range-track {
          height: 8px;
          border-radius: 4px;
        }
      `}</style>
    </div>
  )
}
