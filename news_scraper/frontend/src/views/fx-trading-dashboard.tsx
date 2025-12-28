"use client"

import { useState } from "react"
import {DashboardCard as Card} from "@/components/ui/dashboard-card"

import { Button } from "../components/ui/button"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { TrendingUp, TrendingDown, AlertCircle, Info } from "lucide-react"

type TimePeriod = "1D" | "1W" | "1M" | "1Y" | "YTD"

const chartData = {
  "1D": [
    { time: "09:00", spotRate: 151.15, forwardPoints: 2.48 },
    { time: "10:00", spotRate: 151.18, forwardPoints: 2.45 },
    { time: "11:00", spotRate: 151.22, forwardPoints: 2.42 },
    { time: "12:00", spotRate: 151.25, forwardPoints: 2.38 },
    { time: "13:00", spotRate: 151.27, forwardPoints: 2.35 },
    { time: "14:00", spotRate: 151.29, forwardPoints: 2.32 },
    { time: "15:00", spotRate: 151.31, forwardPoints: 2.28 },
  ],
  "1W": [
    { time: "Mon", spotRate: 150.85, forwardPoints: 2.55 },
    { time: "Tue", spotRate: 150.95, forwardPoints: 2.48 },
    { time: "Wed", spotRate: 151.05, forwardPoints: 2.42 },
    { time: "Thu", spotRate: 151.18, forwardPoints: 2.35 },
    { time: "Fri", spotRate: 151.31, forwardPoints: 2.28 },
  ],
  "1M": [
    { time: "Week 1", spotRate: 149.5, forwardPoints: 2.75 },
    { time: "Week 2", spotRate: 150.2, forwardPoints: 2.6 },
    { time: "Week 3", spotRate: 150.8, forwardPoints: 2.45 },
    { time: "Week 4", spotRate: 151.31, forwardPoints: 2.28 },
  ],
  "1Y": [
    { time: "Q1", spotRate: 145.2, forwardPoints: 3.2 },
    { time: "Q2", spotRate: 148.1, forwardPoints: 2.85 },
    { time: "Q3", spotRate: 149.8, forwardPoints: 2.55 },
    { time: "Q4", spotRate: 151.31, forwardPoints: 2.28 },
  ],
  YTD: [
    { time: "Jan", spotRate: 145.2, forwardPoints: 3.2 },
    { time: "Feb", spotRate: 146.5, forwardPoints: 3.05 },
    { time: "Mar", spotRate: 148.1, forwardPoints: 2.85 },
    { time: "Apr", spotRate: 149.0, forwardPoints: 2.7 },
    { time: "May", spotRate: 149.8, forwardPoints: 2.55 },
    { time: "Jun", spotRate: 151.31, forwardPoints: 2.28 },
  ],
}

const eventTypes = {
  Bullish: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  Alert: "bg-red-500/10 text-red-400 border-red-500/20",
  Bearish: "bg-orange-500/10 text-orange-400 border-orange-500/20",
  Update: "bg-teal-500/10 text-teal-400 border-teal-500/20",
}

const events = [
  {
    type: "Bullish" as const,
    title: "Fed holds rates steady, signals patience on cuts.",
    source: "Global Market",
    time: "2 hrs ago",
    notional: 5000000,
    rate: 151.31,
  },
  {
    type: "Alert" as const,
    title: "EUR/USD P&L decreased to -0.85% today.",
    source: "Related Trade",
    time: "5 min ago",
    notional: 5000000,
    rate: 1.0825,
  },
  {
    type: "Bearish" as const,
    title: "Japan's Q4 GDP revised lower, stoking recession fears.",
    source: "Global Market",
    time: "12 hrs ago",
    notional: null,
    rate: null,
  },
  {
    type: "Update" as const,
    title: "GBP/JPY P&L up +1.50% following market movements.",
    source: "Related Trade",
    time: "1 day ago",
    notional: 3000000,
    rate: 188.1,
  },
  {
    type: "Update" as const,
    title: "US CPI data higher than expected, strengthening USD.",
    source: "Global Market",
    time: "1 hour ago",
    notional: null,
    rate: null,
  },
  {
    type: "Update" as const,
    title: "USD/CHF shows modest gain of +0.20% today.",
    source: "Related Trade",
    time: "2 hours ago",
    notional: 7500000,
    rate: 0.8915,
  },
  {
    type: "Bearish" as const,
    title: "BOJ maintains ultra-loose policy, weakening JPY.",
    source: "Global Market",
    time: "3 hours ago",
    notional: null,
    rate: null,
  },
]

export function FXTradingDashboard() {
  const [selectedPeriod, setSelectedPeriod] = useState<TimePeriod>("1D")

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0b1623] via-[#0d1a28] to-[#0b1623] p-4 md:p-6 lg:p-8">
      {/* Header */}
      <div className="mb-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <h1 className="text-2xl md:text-3xl font-bold text-white">FX-USDJPY-2401-0786</h1>
        <div className="flex gap-2">
          <Button className="bg-teal-500 hover:bg-teal-600 text-white transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-teal-500/30">
            Buy
          </Button>
          <Button className="bg-red-500 hover:bg-red-600 text-white transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-red-500/30">
            Sell
          </Button>
          <Button
            variant="outline"
            className="border-teal-500/50 text-teal-400 hover:bg-teal-500/10 hover:border-teal-500 transition-all duration-300 hover:scale-105 bg-transparent"
          >
            Compare
          </Button>
        </div>
      </div>

      {/* Top Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {/* Current & Forward Rate */}
        <Card className="bg-[#0d1f2d]/80 backdrop-blur-sm border-teal-900/30 p-4 transition-all duration-300 hover:border-teal-500/50 hover:shadow-lg hover:shadow-teal-500/10 hover:scale-[1.02] group">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-xs text-gray-400 mb-1">Current Rate</div>
              <div className="text-2xl font-bold text-white group-hover:text-teal-400 transition-colors">151.31</div>
            </div>
            <div>
              <div className="text-xs text-gray-400 mb-1">Forward Rate</div>
              <div className="text-2xl font-bold text-white group-hover:text-teal-400 transition-colors">151.31</div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-teal-900/30">
            <div>
              <div className="text-xs text-gray-400 mb-1">Execution Rate</div>
              <div className="text-sm text-white flex items-center gap-1">
                149.52
                <span className="text-emerald-400 text-xs flex items-center">
                  <TrendingUp className="w-3 h-3" />
                  +1.10%
                </span>
              </div>
            </div>
            <div>
              <div className="text-xs text-gray-400 mb-1">Portfolio Exposure</div>
              <div className="text-white">151.31</div>
            </div>
          </div>
        </Card>

        {/* Notional */}
        <Card className="bg-[#0d1f2d]/80 backdrop-blur-sm border-teal-900/30 p-4 transition-all duration-300 hover:border-teal-500/50 hover:shadow-lg hover:shadow-teal-500/10 hover:scale-[1.02] group">
          <div className="text-xs text-gray-400 mb-2">Notional</div>
          <div className="text-2xl font-bold text-white mb-4 group-hover:text-teal-400 transition-colors">
            $10,00,000
          </div>
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div>
              <div className="text-gray-400 mb-1">P&L</div>
              <div className="text-white">$2.25</div>
            </div>
            <div>
              <div className="text-gray-400 mb-1">Unrealized P&L</div>
              <div className="text-white">$2.25</div>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-2 text-xs mt-3 pt-3 border-t border-teal-900/30">
            <div>
              <div className="text-gray-400 mb-1">Avg. Buy Price</div>
              <div className="text-white">$2,150.25</div>
            </div>
            <div>
              <div className="text-gray-400 mb-1">Avg. Sell Price</div>
              <div className="text-emerald-400">+$1,120.75</div>
            </div>
            <div>
              <div className="text-gray-400 mb-1">Portfolio Exposure</div>
              <div className="text-white">15.5%</div>
            </div>
          </div>
        </Card>

        {/* Trade Ticket */}
        <Card className="bg-[#0d1f2d]/80 backdrop-blur-sm border-teal-900/30 p-4 lg:col-span-2 transition-all duration-300 hover:border-teal-500/50 hover:shadow-lg hover:shadow-teal-500/10 hover:scale-[1.02]">
          <div className="text-sm font-semibold text-white mb-4">Trade Ticket</div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
            <div>
              <div className="text-gray-400 mb-1">Trade Type</div>
              <div className="text-white font-medium">Spot</div>
            </div>
            <div>
              <div className="text-gray-400 mb-1">Spot Rate</div>
              <div className="text-white font-medium">149.50</div>
            </div>
            <div>
              <div className="text-gray-400 mb-1">Deal Side</div>
              <div className="text-white font-medium">Buy</div>
            </div>
            <div>
              <div className="text-gray-400 mb-1">Notional</div>
              <div className="text-white font-medium">$10,000,000</div>
            </div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs mt-3">
            <div>
              <div className="text-gray-400 mb-1">Forward Points</div>
              <div className="text-white font-medium">+2.0</div>
            </div>
            <div>
              <div className="text-gray-400 mb-1">Execution Point / Venue</div>
              <div className="text-white font-medium">FXALL</div>
            </div>
            <div>
              <div className="text-gray-400 mb-1">Execution Rate</div>
              <div className="text-white font-medium">149.52</div>
            </div>
            <div>
              <div className="text-gray-400 mb-1">Alt'n Rate</div>
              <div className="text-white font-medium">$50.00</div>
            </div>
            <div>
              <div className="text-gray-400 mb-1">Commission</div>
              <div className="text-white font-medium">149.52</div>
            </div>
          </div>
        </Card>
      </div>

      {/* Chart and Event Feed Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Chart Section */}
        <Card className="bg-[#0d1f2d]/80 backdrop-blur-sm border-teal-900/30 p-4 lg:col-span-2 transition-all duration-300 hover:border-teal-500/50 hover:shadow-lg hover:shadow-teal-500/10">
          {/* Time Period Selector */}
          <div className="flex gap-2 mb-4">
            {(["1D", "1W", "1M", "1Y", "YTD"] as TimePeriod[]).map((period) => (
              <button
                key={period}
                onClick={() => setSelectedPeriod(period)}
                className={`px-3 py-1 text-xs rounded transition-all duration-300 ${
                  selectedPeriod === period
                    ? "bg-teal-500 text-white shadow-lg shadow-teal-500/30"
                    : "bg-[#145b5b]/30 text-gray-400 hover:bg-[#145b5b]/50 hover:text-teal-300"
                }`}
              >
                {period}
              </button>
            ))}
          </div>

          {/* Chart */}
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData[selectedPeriod]}>
                <CartesianGrid strokeDasharray="3 3" stroke="#145b5b" opacity={0.2} />
                <XAxis dataKey="time" stroke="#6b7280" tick={{ fill: "#9ca3af", fontSize: 12 }} />
                <YAxis
                  stroke="#6b7280"
                  tick={{ fill: "#9ca3af", fontSize: 12 }}
                  domain={["auto", "auto"]}
                  yAxisId="left"
                />
                <YAxis
                  stroke="#6b7280"
                  tick={{ fill: "#9ca3af", fontSize: 12 }}
                  domain={["auto", "auto"]}
                  yAxisId="right"
                  orientation="right"
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0d1f2d",
                    border: "1px solid #145b5b",
                    borderRadius: "8px",
                    color: "#fff",
                  }}
                  labelStyle={{ color: "#00c7a5" }}
                />
                <Line
                  type="monotone"
                  dataKey="spotRate"
                  stroke="#00c7a5"
                  strokeWidth={2.5}
                  dot={false}
                  yAxisId="left"
                  name="Spot Rate"
                />
                <Line
                  type="monotone"
                  dataKey="forwardPoints"
                  stroke="#00c7a5"
                  strokeWidth={2.5}
                  strokeDasharray="8 8"
                  dot={false}
                  yAxisId="right"
                  name="Forward Points"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Metrics Below Chart */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 pt-4 border-t border-teal-900/30">
            <div className="group cursor-pointer transition-all duration-300 hover:scale-105">
              <div className="text-xs text-gray-400 mb-1">Spot Rate</div>
              <div className="text-lg font-semibold text-white group-hover:text-teal-400 transition-colors">
                151.31
                <span className="text-red-400 text-xs ml-2">-0.12%</span>
              </div>
            </div>
            <div className="group cursor-pointer transition-all duration-300 hover:scale-105">
              <div className="text-xs text-gray-400 mb-1">Forward Points</div>
              <div className="text-lg font-semibold text-white group-hover:text-teal-400 transition-colors">
                +2.5
                <span className="text-emerald-400 text-xs ml-2">+0.05%</span>
              </div>
            </div>
            <div className="group cursor-pointer transition-all duration-300 hover:scale-105">
              <div className="text-xs text-gray-400 mb-1">Premium</div>
              <div className="text-lg font-semibold text-white group-hover:text-teal-400 transition-colors">
                $1,500
                <span className="text-red-400 text-xs ml-2">-0.01%</span>
              </div>
            </div>
            <div className="group cursor-pointer transition-all duration-300 hover:scale-105">
              <div className="text-xs text-gray-400 mb-1">Implied Volatility</div>
              <div className="text-lg font-semibold text-white group-hover:text-teal-400 transition-colors">
                8.2%
                <span className="text-emerald-400 text-xs ml-2">+0.03%</span>
              </div>
            </div>
          </div>
        </Card>

        {/* Cross-Portfolio Event Feed */}
        <Card className="bg-[#0d1f2d]/80 backdrop-blur-sm border-teal-900/30 p-4 transition-all duration-300 hover:border-teal-500/50 hover:shadow-lg hover:shadow-teal-500/10">
          <h3 className="text-sm font-semibold text-white mb-4">Cross-Portfolio Event Feed</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto pr-2 custom-scrollbar">
            {events.slice(0, 5).map((event, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg border transition-all duration-300 hover:scale-[1.02] hover:shadow-md cursor-pointer ${eventTypes[event.type]}`}
              >
                <div className="flex items-start gap-2 mb-1">
                  {event.type === "Bullish" && <TrendingUp className="w-4 h-4 mt-0.5 flex-shrink-0" />}
                  {event.type === "Alert" && <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />}
                  {event.type === "Bearish" && <TrendingDown className="w-4 h-4 mt-0.5 flex-shrink-0" />}
                  {event.type === "Update" && <Info className="w-4 h-4 mt-0.5 flex-shrink-0" />}
                  <div className="flex-1">
                    <p className="text-xs font-medium leading-tight mb-1">{event.title}</p>
                    <div className="flex items-center justify-between text-xs opacity-70">
                      <span>{event.source}</span>
                      <span>{event.time}</span>
                    </div>
                  </div>
                </div>
                {event.notional && event.rate && (
                  <div className="flex justify-between text-xs mt-2 pt-2 border-t border-current/20">
                    <span>Notional: ${(event.notional / 1000000).toFixed(1)}M</span>
                    <span>Rate: {event.rate}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Bottom Row - Risk Tracking, Advised Actions, More Events */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Tracking */}
        <Card className="bg-[#0d1f2d]/80 backdrop-blur-sm border-teal-900/30 p-4 transition-all duration-300 hover:border-teal-500/50 hover:shadow-lg hover:shadow-teal-500/10">
          <h3 className="text-sm font-semibold text-white mb-4">Risk Tracking</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-2 rounded hover:bg-teal-500/5 transition-colors cursor-pointer group">
              <span className="text-xs text-gray-400 group-hover:text-teal-300">Volatility</span>
              <span className="text-sm font-semibold text-white group-hover:text-teal-400">18.5%</span>
            </div>
            <div className="flex justify-between items-center p-2 rounded hover:bg-teal-500/5 transition-colors cursor-pointer group">
              <span className="text-xs text-gray-400 group-hover:text-teal-300">Value at Risk (VaR 95%)</span>
              <span className="text-sm font-semibold text-white group-hover:text-teal-400">$1250</span>
            </div>
            <div className="flex justify-between items-center p-2 rounded hover:bg-teal-500/5 transition-colors cursor-pointer group">
              <span className="text-xs text-gray-400 group-hover:text-teal-300">Delta Exposure</span>
              <span className="text-sm font-semibold text-white group-hover:text-teal-400">$212 K per 1%</span>
            </div>
            <div className="flex justify-between items-center p-2 rounded hover:bg-teal-500/5 transition-colors cursor-pointer group">
              <span className="text-xs text-gray-400 group-hover:text-teal-300">Hedge Ratio</span>
              <span className="text-sm font-semibold text-white group-hover:text-teal-400">85/100</span>
            </div>
            <div className="flex justify-between items-center p-2 rounded hover:bg-teal-500/5 transition-colors cursor-pointer group">
              <span className="text-xs text-gray-400 group-hover:text-teal-300">Counterparty Exposure</span>
              <span className="text-sm font-semibold text-white group-hover:text-teal-400">27%</span>
            </div>
            <div className="flex justify-between items-center p-2 rounded hover:bg-teal-500/5 transition-colors cursor-pointer group">
              <span className="text-xs text-gray-400 group-hover:text-teal-300">Utilization Limit</span>
              <span className="text-sm font-semibold text-white group-hover:text-teal-400">60%</span>
            </div>
            <div className="flex justify-between items-center p-2 rounded hover:bg-teal-500/5 transition-colors cursor-pointer group">
              <span className="text-xs text-gray-400 group-hover:text-teal-300">Correlation Impact</span>
              <span className="text-sm font-semibold text-white group-hover:text-teal-400">0.6</span>
            </div>
          </div>
        </Card>

        {/* Advised Actions */}
        <Card className="bg-[#0d1f2d]/80 backdrop-blur-sm border-teal-900/30 p-4 transition-all duration-300 hover:border-teal-500/50 hover:shadow-lg hover:shadow-teal-500/10">
          <h3 className="text-sm font-semibold text-white mb-4">Advised Actions</h3>
          <div className="space-y-4">
            <div className="p-3 bg-teal-500/5 border border-teal-500/20 rounded-lg transition-all duration-300 hover:bg-teal-500/10 hover:scale-[1.02] cursor-pointer">
              <div className="text-xs font-medium text-teal-400 mb-1">Hedge Action</div>
              <p className="text-xs text-gray-300 leading-relaxed">
                "Increase USD hedge rate from 70% to 85%, given strengthening USD trend."
              </p>
            </div>
            <div className="p-3 bg-orange-500/5 border border-orange-500/20 rounded-lg transition-all duration-300 hover:bg-orange-500/10 hover:scale-[1.02] cursor-pointer">
              <div className="text-xs font-medium text-orange-400 mb-1">Liquidity Alert</div>
              <p className="text-xs text-gray-300 leading-relaxed">
                "Market depth &lt; 12 shows USD shortfall; suggest booking smaller tranches."
              </p>
            </div>
            <div className="p-3 bg-blue-500/5 border border-blue-500/20 rounded-lg transition-all duration-300 hover:bg-blue-500/10 hover:scale-[1.02] cursor-pointer">
              <div className="text-xs font-medium text-blue-400 mb-1">Macro Outlook</div>
              <p className="text-xs text-gray-300 leading-relaxed">
                "Fed pause confirmed; neutral bias. Expected USD/JPY range: 82.00 - 83.50."
              </p>
            </div>
          </div>
        </Card>

        {/* Extended Event Feed */}
        <Card className="bg-[#0d1f2d]/80 backdrop-blur-sm border-teal-900/30 p-4 transition-all duration-300 hover:border-teal-500/50 hover:shadow-lg hover:shadow-teal-500/10">
          <h3 className="text-sm font-semibold text-white mb-4">Recent Events</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto pr-2 custom-scrollbar">
            {events.slice(5).map((event, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg border transition-all duration-300 hover:scale-[1.02] hover:shadow-md cursor-pointer ${eventTypes[event.type]}`}
              >
                <div className="flex items-start gap-2 mb-1">
                  {event.type === "Bullish" && <TrendingUp className="w-4 h-4 mt-0.5 flex-shrink-0" />}
                  {event.type === "Alert" && <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />}
                  {event.type === "Bearish" && <TrendingDown className="w-4 h-4 mt-0.5 flex-shrink-0" />}
                  {event.type === "Update" && <Info className="w-4 h-4 mt-0.5 flex-shrink-0" />}
                  <div className="flex-1">
                    <p className="text-xs font-medium leading-tight mb-1">{event.title}</p>
                    <div className="flex items-center justify-between text-xs opacity-70">
                      <span>{event.source}</span>
                      <span>{event.time}</span>
                    </div>
                  </div>
                </div>
                {event.notional && event.rate && (
                  <div className="flex justify-between text-xs mt-2 pt-2 border-t border-current/20">
                    <span>Notional: ${(event.notional / 1000000).toFixed(1)}M</span>
                    <span>Rate: {event.rate}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>
      </div>

      <style >{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(20, 91, 91, 0.1);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(0, 199, 165, 0.3);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(0, 199, 165, 0.5); 
        }
      `}</style>
    </div>
  )
}
