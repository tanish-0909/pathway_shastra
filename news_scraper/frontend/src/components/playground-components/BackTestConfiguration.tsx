"use client"

import { Calendar, ChevronDown } from "lucide-react"
import { useState } from "react"

export default function BacktestConfiguration() {
  const [startDate, setStartDate] = useState("2022-01-01")
  const [endDate, setEndDate] = useState("2023-12-31")
  const [strategyType, setStrategyType] = useState("Mean Reversion")
  const [lookbackPeriod, setLookbackPeriod] = useState("20")

  return (
    <div className="w-full max-w-5xl mx-auto bg-[#0f2e2e] rounded-3xl p-10 shadow-2xl">
      {/* Header */}
      <div className="mb-10">
        <h1 className="text-white text-4xl font-bold mb-2">Backtest Configuration</h1>
        <p className="text-gray-400 text-lg">Historical FI/FX Strategy</p>
      </div>

      {/* Form Grid */}
      <div className="grid grid-cols-2 gap-x-12 gap-y-8 mb-8">
        {/* Start Date */}
        <div>
          <label className="block text-white text-lg mb-3">Start Date</label>
          <div className="relative">
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full bg-transparent border border-gray-600 rounded-xl px-5 py-4 text-white text-lg focus:outline-none focus:border-teal-500"
            />
            <Calendar className="absolute right-5 top-1/2 -translate-y-1/2 text-gray-500 w-5 h-5 pointer-events-none" />
          </div>
        </div>

        {/* End Date */}
        <div>
          <label className="block text-white text-lg mb-3">End Date</label>
          <div className="relative">
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full bg-transparent border border-gray-600 rounded-xl px-5 py-4 text-white text-lg focus:outline-none focus:border-teal-500"
            />
            <Calendar className="absolute right-5 top-1/2 -translate-y-1/2 text-gray-500 w-5 h-5 pointer-events-none" />
          </div>
        </div>

        {/* Strategy Type */}
        <div>
          <label className="block text-white text-lg mb-3">Strategy Type</label>
          <div className="relative">
            <select
              value={strategyType}
              onChange={(e) => setStrategyType(e.target.value)}
              className="w-full bg-transparent border border-gray-600 rounded-xl px-5 py-4 text-white text-lg appearance-none focus:outline-none focus:border-teal-500"
            >
              <option value="Mean Reversion" className="bg-[#0f2e2e]">
                Mean Reversion
              </option>
            </select>
            <ChevronDown className="absolute right-5 top-1/2 -translate-y-1/2 text-gray-500 w-5 h-5 pointer-events-none" />
          </div>
        </div>

        {/* Lookback Period */}
        <div>
          <label className="block text-white text-lg mb-3">Lookback Period</label>
          <div className="relative">
            <input
              type="number"
              value={lookbackPeriod}
              onChange={(e) => setLookbackPeriod(e.target.value)}
              className="w-full bg-transparent border border-gray-600 rounded-xl px-5 py-4 text-white text-lg focus:outline-none focus:border-teal-500"
            />
            <span className="absolute right-5 top-1/2 -translate-y-1/2 text-gray-500 text-lg">Days</span>
          </div>
        </div>
      </div>

      {/* Run Backtest Button */}
      <button className="w-full bg-teal-600 hover:bg-teal-700 text-white text-xl font-semibold py-5 rounded-xl transition-colors mb-12">
        Run Backtest
      </button>

      {/* Equity Curve Section */}
      <div>
        <h2 className="text-white text-2xl font-semibold mb-4">Equity Curve</h2>
        <div className="mb-6">
          <div className="text-white text-sm mb-1">
            CAGR: <span className="font-semibold">12.5%</span>
          </div>
          <div className="text-white text-sm">
            Max DD: <span className="font-semibold">-5%</span>
          </div>
        </div>

        {/* Chart Area */}
        <div className="relative h-96 bg-gradient-to-b from-[#0a2323]/50 to-[#0a2323]/20 rounded-lg overflow-hidden">
          <svg className="w-full h-full" viewBox="0 0 1000 400" preserveAspectRatio="none">
            {/* Area fill */}
            <path
              d="M 0 380 L 0 300 L 150 250 L 300 220 L 380 240 L 450 200 L 600 150 L 750 120 L 900 80 L 1000 50 L 1000 380 Z"
              fill="url(#gradient)"
              opacity="0.3"
            />
            {/* Line */}
            <path
              d="M 0 300 L 150 250 L 300 220 L 380 240 L 450 200 L 600 150 L 750 120 L 900 80 L 1000 50"
              stroke="#14b8a6"
              strokeWidth="3"
              fill="none"
            />
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#14b8a6" stopOpacity="0.5" />
                <stop offset="100%" stopColor="#14b8a6" stopOpacity="0" />
              </linearGradient>
            </defs>
          </svg>
        </div>
      </div>
    </div>
  )
}
