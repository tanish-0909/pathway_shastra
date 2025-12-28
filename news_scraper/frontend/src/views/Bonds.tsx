"use client"

import React from "react"
import { TrendingUp, Calendar } from "lucide-react"
import { useAsset } from "@/context/AssetContext"

// Data structures
interface BondInfo {
  name: string
  cusip: string
  isin: string
  figi: string
  rating: string
}

interface CouponInfo {
  rate: string
  frequency: string
  maturityDate: string
  nextCouponDate: string
  minimumIncrement: string
  settlementType: string
}

interface PriceInfo {
  lastPrice: number
  change: string
  bidPrice: number
  askPrice: number
  spread: number
  cleanPrice: number
  dirtyPrice: number
  accruedInterest: number
}

interface RiskMetrics {
  duration: string
  convexity: string
  dv01: string
  oas: string
  zSpread: string
  var: string
}

interface ChartMetrics {
  currentYielding: string
  oneMonthChange: string
  volatility: string
  maxDrawdown: string
}

interface NewsItem {
  title: string
  source: string
  time: string
  icon: string
}

interface PortfolioImpact {
  allocation: string
  portfolioYieldDelta: string
}

interface CashFlowRow {
  paymentDate: string
  type: string
  couponPercent: number
  days: number
  principal: string
  totalPayment: string
}

// Mock data constants
const BOND_INFO: BondInfo = {
  name: "Gulf Oil Corp – 8.5% (Fixed, Semi Annual)",
  cusip: "40246A AB5",
  isin: "USGULF2040N8",
  figi: "B0OGULF8X9Y1",
  rating: "BBB (S&P)",
}

const COUPON_INFO: CouponInfo = {
  rate: "8.50%",
  frequency: "Semi - Annual",
  maturityDate: "2040-10-15",
  nextCouponDate: "15 Apr 2026",
  minimumIncrement: "$1,000",
  settlementType: "T+2",
}

const PRICE_INFO: PriceInfo = {
  lastPrice: 105.0,
  change: "-0.10%",
  bidPrice: 104.7,
  askPrice: 105.3,
  spread: 0.6,
  cleanPrice: 105.0,
  dirtyPrice: 105.57,
  accruedInterest: 0.57,
}

const RISK_METRICS: RiskMetrics = {
  duration: "15 Y",
  convexity: "1.85",
  dv01: "$4,725 per bp",
  oas: "+260 bps",
  zSpread: "+245 bps",
  var: "$45,000",
}

interface ChartDataPoint {
  x: number
  y1: number
  y2: number
}

const CHART_DATA: Record<string, { points: ChartDataPoint[]; metrics: ChartMetrics }> = {
  "1D": {
    points: [
      { x: 0, y1: 80, y2: 120 },
      { x: 100, y1: 75, y2: 110 },
      { x: 200, y1: 90, y2: 125 },
      { x: 300, y1: 85, y2: 115 },
      { x: 400, y1: 70, y2: 135 },
      { x: 500, y1: 60, y2: 145 },
      { x: 600, y1: 55, y2: 160 },
    ],
    metrics: {
      currentYielding: "7.90%",
      oneMonthChange: "+18 bps",
      volatility: "0.71%",
      maxDrawdown: "+2.0%",
    },
  },
  "1W": {
    points: [
      { x: 0, y1: 85, y2: 115 },
      { x: 100, y1: 80, y2: 120 },
      { x: 200, y1: 75, y2: 110 },
      { x: 300, y1: 82, y2: 118 },
      { x: 400, y1: 78, y2: 122 },
      { x: 500, y1: 70, y2: 130 },
      { x: 600, y1: 65, y2: 135 },
    ],
    metrics: {
      currentYielding: "7.85%",
      oneMonthChange: "+15 bps",
      volatility: "0.68%",
      maxDrawdown: "+1.8%",
    },
  },
  "1M": {
    points: [
      { x: 0, y1: 95, y2: 105 },
      { x: 100, y1: 88, y2: 112 },
      { x: 200, y1: 82, y2: 118 },
      { x: 300, y1: 78, y2: 122 },
      { x: 400, y1: 75, y2: 125 },
      { x: 500, y1: 68, y2: 132 },
      { x: 600, y1: 60, y2: 140 },
    ],
    metrics: {
      currentYielding: "7.92%",
      oneMonthChange: "+22 bps",
      volatility: "0.75%",
      maxDrawdown: "+2.2%",
    },
  },
  "1Y": {
    points: [
      { x: 0, y1: 110, y2: 90 },
      { x: 100, y1: 105, y2: 95 },
      { x: 200, y1: 95, y2: 105 },
      { x: 300, y1: 88, y2: 112 },
      { x: 400, y1: 80, y2: 120 },
      { x: 500, y1: 70, y2: 130 },
      { x: 600, y1: 55, y2: 145 },
    ],
    metrics: {
      currentYielding: "7.88%",
      oneMonthChange: "+45 bps",
      volatility: "0.82%",
      maxDrawdown: "+3.5%",
    },
  },
  YTD: {
    points: [
      { x: 0, y1: 100, y2: 100 },
      { x: 100, y1: 92, y2: 108 },
      { x: 200, y1: 87, y2: 113 },
      { x: 300, y1: 83, y2: 117 },
      { x: 400, y1: 76, y2: 124 },
      { x: 500, y1: 68, y2: 132 },
      { x: 600, y1: 58, y2: 142 },
    ],
    metrics: {
      currentYielding: "7.91%",
      oneMonthChange: "+38 bps",
      volatility: "0.78%",
      maxDrawdown: "+2.9%",
    },
  },
}

const ALL_CASH_FLOW_DATA: CashFlowRow[] = [
  {
    paymentDate: "2025-04-15",
    type: "Coupon",
    couponPercent: 8.5,
    days: 183,
    principal: "$0.00",
    totalPayment: "$42.50",
  },
  {
    paymentDate: "2025-10-15",
    type: "Coupon",
    couponPercent: 8.5,
    days: 182,
    principal: "$0.00",
    totalPayment: "$42.50",
  },
  {
    paymentDate: "2026-04-15",
    type: "Coupon",
    couponPercent: 8.5,
    days: 183,
    principal: "$0.00",
    totalPayment: "$42.50",
  },
  {
    paymentDate: "2026-10-15",
    type: "Coupon",
    couponPercent: 8.5,
    days: 182,
    principal: "$0.00",
    totalPayment: "$42.50",
  },
  {
    paymentDate: "2027-04-15",
    type: "Coupon",
    couponPercent: 8.5,
    days: 183,
    principal: "$0.00",
    totalPayment: "$42.50",
  },
  {
    paymentDate: "2027-10-15",
    type: "Coupon",
    couponPercent: 8.5,
    days: 182,
    principal: "$0.00",
    totalPayment: "$42.50",
  },
  {
    paymentDate: "2028-04-15",
    type: "Coupon",
    couponPercent: 8.5,
    days: 183,
    principal: "$0.00",
    totalPayment: "$42.50",
  },
  {
    paymentDate: "2040-04-15",
    type: "Coupon",
    couponPercent: 8.5,
    days: 183,
    principal: "$0.00",
    totalPayment: "$42.50",
  },
  {
    paymentDate: "2040-10-15",
    type: "Coupon + Principal",
    couponPercent: 8.5,
    days: 183,
    principal: "$1,000",
    totalPayment: "$1,042.50",
  },
]

const NEWS_ITEMS: NewsItem[] = [
  {
    title: "Moody's maintains BBB rating - Supports Credit Stability",
    source: "Internal Update",
    time: "2 h ago",
    icon: "chart",
  },
  {
    title: "OPEC extends production cuts - Slight Spread Widening",
    source: "reuters",
    time: "3 hours ago",
    icon: "building",
  },
  {
    title: "Fed hints at data-dependent cuts - Lowers yields by 10 bps",
    source: "Bloomberg",
    time: "5 hours ago",
    icon: "building",
  },
]

const PORTFOLIO_IMPACT: PortfolioImpact = {
  allocation: "2.5%",
  portfolioYieldDelta: "+0.03%",
}

const SUMMARY_TEXT =
  "The Gulf Oil Corp 2040 bond offers a high fixed coupon with moderate credit risk. Its long 15-year duration makes it rate-sensitive, while spreads reflect stable BBB credit quality. Key risks arise from yield curve volatility and oil-market headlines influencing spreads and VaR exposure."

// Main Component
export const Bonds: React.FC = () => {
  const { selectedAsset } = useAsset()
  const [selectedTimePeriod, setSelectedTimePeriod] = React.useState("1D")
  const [selectedTimeFilter, setSelectedTimeFilter] = React.useState("All")
  const [selectedTypeFilter, setSelectedTypeFilter] = React.useState("All Types")
  const [dateRange, setDateRange] = React.useState<{ start: string; end: string } | null>(null)
  const [showDatePicker, setShowDatePicker] = React.useState(false)

  const timePeriods = ["1D", "1W", "1M", "1Y", "YTD"]
  const cashFlowTabs = ["All", "Upcoming", "Past", "All Types", "Coupon", "Principal"]

  // Create bond info from selected asset or use default
  const bondInfo: BondInfo = selectedAsset && selectedAsset.assetType === 'bonds'
    ? {
        name: `${selectedAsset.name} – ${selectedAsset.coupon || '8.5%'} (Fixed, Semi Annual)`,
        cusip: `CUSIP-${selectedAsset.id}`,
        isin: `ISIN-${selectedAsset.ticker}`,
        figi: `FIGI-${selectedAsset.id}`,
        rating: "BBB (S&P)",
      }
    : BOND_INFO

  // Create coupon info from selected asset or use default
  const couponInfo: CouponInfo = selectedAsset && selectedAsset.assetType === 'bonds'
    ? {
        rate: selectedAsset.coupon || COUPON_INFO.rate,
        frequency: "Semi - Annual",
        maturityDate: selectedAsset.maturityDate || COUPON_INFO.maturityDate,
        nextCouponDate: COUPON_INFO.nextCouponDate,
        minimumIncrement: "$1,000",
        settlementType: "T+2",
      }
    : COUPON_INFO

  // Create price info from selected asset or use default
  const priceInfo: PriceInfo = selectedAsset && selectedAsset.assetType === 'bonds'
    ? {
        lastPrice: selectedAsset.priceOfPar || PRICE_INFO.lastPrice,
        change: `${selectedAsset.changeBps && selectedAsset.changeBps >= 0 ? '+' : ''}${selectedAsset.changeBps || 0} bps`,
        bidPrice: (selectedAsset.priceOfPar || PRICE_INFO.lastPrice) - 0.3,
        askPrice: (selectedAsset.priceOfPar || PRICE_INFO.lastPrice) + 0.3,
        spread: 0.6,
        cleanPrice: selectedAsset.priceOfPar || PRICE_INFO.cleanPrice,
        dirtyPrice: (selectedAsset.priceOfPar || PRICE_INFO.cleanPrice) + 0.57,
        accruedInterest: 0.57,
      }
    : PRICE_INFO

  // Create risk metrics from selected asset or use default
  const riskMetrics: RiskMetrics = selectedAsset && selectedAsset.assetType === 'bonds'
    ? {
        duration: typeof selectedAsset.duration === 'number' 
          ? `${selectedAsset.duration} Y` 
          : (selectedAsset.duration || RISK_METRICS.duration),
        convexity: RISK_METRICS.convexity,
        dv01: RISK_METRICS.dv01,
        oas: RISK_METRICS.oas,
        zSpread: RISK_METRICS.zSpread,
        var: RISK_METRICS.var,
      }
    : RISK_METRICS

  const currentChartData = CHART_DATA[selectedTimePeriod]

  const getFilteredCashFlowData = () => {
    let filtered = [...ALL_CASH_FLOW_DATA]
    const today = new Date()

    if (selectedTimeFilter === "Upcoming") {
      filtered = filtered.filter((row) => new Date(row.paymentDate) >= today)
    } else if (selectedTimeFilter === "Past") {
      filtered = filtered.filter((row) => new Date(row.paymentDate) < today)
    }

    if (selectedTypeFilter === "Coupon") {
      filtered = filtered.filter((row) => row.type === "Coupon")
    } else if (selectedTypeFilter === "Principal") {
      filtered = filtered.filter((row) => row.type.includes("Principal"))
    }

    if (dateRange) {
      const startDate = new Date(dateRange.start)
      const endDate = new Date(dateRange.end)
      filtered = filtered.filter((row) => {
        const paymentDate = new Date(row.paymentDate)
        return paymentDate >= startDate && paymentDate <= endDate
      })
    }

    return filtered
  }

  const filteredCashFlowData = getFilteredCashFlowData()

  return (
    <div className="min-h-screen bg-background text-white p-6">
      {/* Title and Actions */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">{bondInfo.name}</h1>
          <p className="text-sm text-white/70">
            CUSIP: {bondInfo.cusip} / ISIN: {bondInfo.isin} / FIGI: {bondInfo.figi}{" "}
            <span className="text-primary">{bondInfo.rating}</span>
          </p>
        </div>
        <div className="flex gap-3">
          <button className="px-8 py-3 bg-primary hover:bg-primary/80 text-black font-semibold rounded-lg">Buy</button>
          <button className="px-8 py-3 bg-red-500 hover:bg-red-600 text-white font-semibold rounded-lg">Sell</button>
          <button className="px-8 py-3 bg-transparent border-2 border-primary text-primary font-semibold rounded-lg flex items-center gap-2">
            Compare
            <span className="text-xs">▼</span>
          </button>
        </div>
      </div>

      {/* Top Info Cards */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {/* Coupon Info Card */}
        <div className="bg-card border border-border rounded-xl p-6">
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-white/70 text-sm mb-1">Coupon Rate</p>
              <p className="text-3xl font-bold">{couponInfo.rate}</p>
              <p className="text-white/70 text-sm">{couponInfo.frequency}</p>
            </div>
            <div>
              <p className="text-white/70 text-sm mb-1">Maturity Date</p>
              <p className="text-2xl font-bold">{couponInfo.maturityDate}</p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border">
            <div>
              <p className="text-white/70 text-sm mb-1">Next Coupon Date</p>
              <p className="text-xl font-bold">{couponInfo.nextCouponDate}</p>
            </div>
            <div>
              <p className="text-white/70 text-sm mb-1">Minimum Increment</p>
              <p className="text-xl font-bold">{couponInfo.minimumIncrement}</p>
              <p className="text-white/70 text-xs">Settlement Type : {couponInfo.settlementType}</p>
            </div>
          </div>
        </div>

        {/* Price Info Card */}
        <div className="bg-card border border-border rounded-xl p-6">
          <div className="mb-4">
            <div className="flex items-baseline justify-between mb-2">
              <p className="text-white/70 text-sm">Last Price</p>
              <div className="text-right">
                <p className="text-white/70 text-xs">Bid/Ask</p>
                <p className="text-sm">
                  {priceInfo.bidPrice} / {priceInfo.askPrice}
                </p>
              </div>
            </div>
            <div className="flex items-baseline gap-3">
              <p className="text-4xl font-bold">{priceInfo.lastPrice.toFixed(2)}</p>
              <p className="text-red-500 text-sm">{priceInfo.change}</p>
              <p className="text-white/70 text-sm ml-auto">
                Bid - Ask
                <br />
                Spread
                <br />
                {priceInfo.spread.toFixed(2)}
              </p>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4 pt-4 border-t border-border">
            <div>
              <p className="text-white/70 text-xs mb-1">Clean Price</p>
              <p className="text-lg font-bold">{priceInfo.cleanPrice.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-white/70 text-xs mb-1">Dirty Price</p>
              <p className="text-lg font-bold">{priceInfo.dirtyPrice.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-white/70 text-xs mb-1">Accrued Interest</p>
              <p className="text-lg font-bold">${priceInfo.accruedInterest.toFixed(2)}</p>
            </div>
          </div>
        </div>

        {/* Risk Metrics Card */}
        <div className="bg-card border border-border rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Risk Metrics</h3>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-white/70 text-xs mb-1">Duration</p>
              <p className="text-sm font-semibold">{riskMetrics.duration}</p>
            </div>
            <div>
              <p className="text-white/70 text-xs mb-1">Convexity</p>
              <p className="text-sm font-semibold">{riskMetrics.convexity}</p>
            </div>
            <div>
              <p className="text-white/70 text-xs mb-1">DV01</p>
              <p className="text-sm font-semibold">{riskMetrics.dv01}</p>
            </div>
            <div>
              <p className="text-white/70 text-xs mb-1">OAS</p>
              <p className="text-sm font-semibold">{riskMetrics.oas}</p>
            </div>
            <div>
              <p className="text-white/70 text-xs mb-1">Z-Spread</p>
              <p className="text-sm font-semibold">{riskMetrics.zSpread}</p>
            </div>
            <div>
              <p className="text-white/70 text-xs mb-1">VaR</p>
              <p className="text-sm font-semibold">{riskMetrics.var}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Chart and News Section */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {/* Chart Card */}
        <div className="col-span-2 bg-card border border-border rounded-xl p-6">
          {/* Time Period Selector */}
          <div className="flex gap-2 mb-4">
            {timePeriods.map((period) => (
              <button
                key={period}
                onClick={() => setSelectedTimePeriod(period)}
                className={`px-4 py-1 rounded text-sm transition-colors ${
                  selectedTimePeriod === period
                    ? "bg-primary/20 text-primary border border-primary"
                    : "text-white/70 hover:text-primary hover:bg-primary/10"
                }`}
              >
                {period}
              </button>
            ))}
          </div>

          <div className="relative h-64 mb-4">
            <svg className="w-full h-full" viewBox="0 0 600 200">
              {/* Grid lines */}
              {[0, 1, 2, 3, 4].map((i) => (
                <line key={i} x1="0" y1={i * 50} x2="600" y2={i * 50} stroke="#1a2332" strokeWidth="1" />
              ))}
              {/* Dashed line (lower trend) */}
              <polyline
                points={currentChartData.points.map((p) => `${p.x},${p.y2}`).join(" ")}
                fill="none"
                stroke="#4a5568"
                strokeWidth="2"
                strokeDasharray="5,5"
              />
              {/* Solid line (upper trend) */}
              <polyline
                points={currentChartData.points.map((p) => `${p.x},${p.y1}`).join(" ")}
                fill="none"
                stroke="#06b6d4"
                strokeWidth="2"
              />
            </svg>
          </div>

          <div className="grid grid-cols-4 gap-4">
            <div>
              <p className="text-white/70 text-xs mb-1">Current Yielding</p>
              <p className="text-xl font-bold text-primary">{currentChartData.metrics.currentYielding}</p>
            </div>
            <div>
              <p className="text-white/70 text-xs mb-1">1-Month Change</p>
              <p className="text-xl font-bold text-primary">{currentChartData.metrics.oneMonthChange}</p>
            </div>
            <div>
              <p className="text-white/70 text-xs mb-1">Volatility (20 D σ)</p>
              <p className="text-xl font-bold">{currentChartData.metrics.volatility}</p>
            </div>
            <div>
              <p className="text-white/70 text-xs mb-1">Max Drawdown (1 Y)</p>
              <p className="text-xl font-bold text-primary">{currentChartData.metrics.maxDrawdown}</p>
            </div>
          </div>
        </div>

        {/* News Card */}
        <div className="bg-card border border-border rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">News and analytics</h3>
          <div className="space-y-4">
            {NEWS_ITEMS.map((item, index) => (
              <div key={index} className="flex gap-3">
                <div className="w-12 h-12 bg-gray-700 rounded flex-shrink-0 flex items-center justify-center">
                  {item.icon === "chart" ? (
                    <TrendingUp className="w-6 h-6 text-primary" />
                  ) : (
                    <div className="w-6 h-6 bg-gray-600 rounded"></div>
                  )}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium mb-1">{item.title}</p>
                  <p className="text-xs text-white/70">
                    {item.source} • {item.time}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Portfolio Impact and Summary */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {/* Impact on Portfolio */}
        <div className="col-span-2 bg-card border border-border rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Impact on Portfolio</h3>
          <div className="flex justify-between items-center">
            <div>
              <p className="text-white/70 text-sm mb-1">Allocation</p>
              <p className="text-2xl font-bold">{PORTFOLIO_IMPACT.allocation}</p>
            </div>
            <div>
              <p className="text-white/70 text-sm mb-1">Portfolio YieldΔ</p>
              <p className="text-2xl font-bold text-primary">{PORTFOLIO_IMPACT.portfolioYieldDelta}</p>
            </div>
          </div>
        </div>

        {/* Summary */}
        <div className="bg-card border border-border rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-3">Summary</h3>
          <p className="text-xs text-white/70 leading-relaxed">{SUMMARY_TEXT}</p>
        </div>
      </div>

      {/* Cash Flow Schedule */}
      <div className="bg-card border border-border rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4">Coupon & Cash Flow Schedule</h3>

        <div className="flex gap-2 mb-4 flex-wrap">
          {/* Time filters */}
          {["All", "Upcoming", "Past"].map((filter) => (
            <button
              key={filter}
              onClick={() => setSelectedTimeFilter(filter)}
              className={`px-4 py-2 rounded text-sm transition-colors ${
                selectedTimeFilter === filter
                  ? "bg-primary text-black font-semibold"
                  : "bg-gray-700 text-gray-300 hover:bg-gray-600"
              }`}
            >
              {filter}
            </button>
          ))}

          {/* Type filters */}
          {["All Types", "Coupon", "Principal"].map((filter) => (
            <button
              key={filter}
              onClick={() => setSelectedTypeFilter(filter)}
              className={`px-4 py-2 rounded text-sm transition-colors ${
                selectedTypeFilter === filter
                  ? "bg-primary text-black font-semibold"
                  : "bg-gray-700 text-gray-300 hover:bg-gray-600"
              }`}
            >
              {filter}
            </button>
          ))}

          <div className="ml-auto relative">
            <button
              onClick={() => setShowDatePicker(!showDatePicker)}
              className="px-4 py-2 rounded text-sm bg-gray-700 text-gray-300 flex items-center gap-2 hover:bg-gray-600"
            >
              <Calendar className="w-4 h-4" />
              Date Range
              {dateRange && <span className="text-primary">✓</span>}
            </button>

            {showDatePicker && (
              <div className="absolute right-0 top-12 bg-card border border-border rounded-lg p-4 z-10 min-w-[300px]">
                <div className="space-y-3">
                  <div>
                    <label className="text-xs text-white/70 block mb-1">Start Date</label>
                    <input
                      type="date"
                      className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-sm text-white"
                      value={dateRange?.start || ""}
                      onChange={(e) => setDateRange({ start: e.target.value, end: dateRange?.end || e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="text-xs text-white/70 block mb-1">End Date</label>
                    <input
                      type="date"
                      className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-sm text-white"
                      value={dateRange?.end || ""}
                      onChange={(e) => setDateRange({ start: dateRange?.start || e.target.value, end: e.target.value })}
                    />
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => {
                        setDateRange(null)
                        setShowDatePicker(false)
                      }}
                      className="flex-1 px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm"
                    >
                      Clear
                    </button>
                    <button
                      onClick={() => setShowDatePicker(false)}
                      className="flex-1 px-3 py-2 bg-primary hover:bg-primary/80 text-black rounded text-sm font-semibold"
                    >
                      Apply
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 px-4 text-sm font-semibold text-white/70">Payment Date</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-white/70">Type</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-white/70">Coupon %</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-white/70">Days</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-white/70">Principal</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-white/70">Total Payment</th>
              </tr>
            </thead>
            <tbody>
              {filteredCashFlowData.length > 0 ? (
                filteredCashFlowData.map((row, index) => (
                  <tr key={index} className="border-b border-gray-800 hover:bg-gray-800/50 transition-colors">
                    <td className="py-3 px-4 text-sm">{row.paymentDate}</td>
                    <td className="py-3 px-4 text-sm">{row.type}</td>
                    <td className="py-3 px-4 text-sm">{row.couponPercent.toFixed(2)}</td>
                    <td className="py-3 px-4 text-sm">{row.days}</td>
                    <td className="py-3 px-4 text-sm">{row.principal}</td>
                    <td className="py-3 px-4 text-sm font-semibold">{row.totalPayment}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-white/70">
                    No payments match the selected filters
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
