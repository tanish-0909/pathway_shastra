"use client"
import { ChevronRight } from "lucide-react"
import { motion } from "framer-motion"
import { clsx } from "clsx"
import { useAsset } from "@/context/AssetContext"

// Default stock data for fallback
const DEFAULT_STOCK = {
  name: "Apple Inc.",
  ticker: "AAPL",
  price: 178.72,
  change: 2.34,
  changePercent: 1.33,
  marketCap: "2.8T",
  peRatio: 28.5,
  dividend: "0.52%",
  volume: "52.3M",
}

export function Stocks() {
  const { selectedAsset } = useAsset()
  
  // Use selected asset if it's a stock, otherwise use default
  const stockData = selectedAsset && selectedAsset.assetType === 'stocks'
    ? {
        name: selectedAsset.name,
        ticker: selectedAsset.ticker,
        price: selectedAsset.price || DEFAULT_STOCK.price,
        change: selectedAsset.change || DEFAULT_STOCK.change,
        changePercent: selectedAsset.changePercent || DEFAULT_STOCK.changePercent,
        marketCap: selectedAsset.marketCap || DEFAULT_STOCK.marketCap,
        peRatio: selectedAsset.peRatio || DEFAULT_STOCK.peRatio,
        dividend: selectedAsset.dividend || DEFAULT_STOCK.dividend,
        volume: selectedAsset.volume || DEFAULT_STOCK.volume,
      }
    : DEFAULT_STOCK

  const isPositiveChange = (stockData.change || 0) >= 0

  return (
    <div className="min-h-screen bg-background text-white">
      {/* Content Area */}
      <div className="px-8 py-6">
        {/* Price Header */}
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-lg font-semibold text-primary mb-2">{stockData.name} ({stockData.ticker})</h2>
            <div className="flex items-baseline gap-3 mb-1">
              <h1 className="text-4xl font-bold">${stockData.price.toFixed(2)}</h1>
              <span className={`text-sm ${isPositiveChange ? 'text-green-500' : 'text-red-500'}`}>
                {isPositiveChange ? '▲' : '▼'} {isPositiveChange ? '+' : ''}{stockData.changePercent?.toFixed(2)}%
              </span>
              <span className={`text-sm ${isPositiveChange ? 'text-green-500' : 'text-red-500'}`}>
                {isPositiveChange ? '+' : ''}${stockData.change?.toFixed(2)} Today
              </span>
            </div>
            <p className="text-xs text-white/70">{new Date().toLocaleString()} · USD · NASDAQ</p>
          </div>
          <div className="flex gap-3">
            <button className="bg-primary hover:bg-primary/80 text-white px-6 py-2 rounded-lg font-medium transition-colors">
              Buy
            </button>
            <button className="bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded-lg font-medium transition-colors">
              Sell
            </button>
            <button className="border border-primary text-primary hover:bg-primary/80/10 px-6 py-2 rounded-lg font-medium transition-colors flex items-center gap-2">
              Compare
              <ChevronRight size={16} />
            </button>
          </div>
        </div>

        {/* Main Grid */}
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            {/* Current Value Card */}
            <div className="bg-card border border-border rounded-lg p-5">
              <div className="mb-3">
                <p className="text-xs font-medium text-primary uppercase tracking-wide mb-2">Market Data</p>
                <p className={`text-4xl font-bold ${isPositiveChange ? 'text-green-400' : 'text-red-400'}`}>
                  ${stockData.price.toFixed(2)}
                </p>
              </div>
              <div className="grid grid-cols-2 gap-4 pt-3 border-t border-border">
                <div>
                  <p className="text-xs text-white/70 mb-1">Market Cap</p>
                  <p className="text-lg font-semibold text-white">{stockData.marketCap}</p>
                </div>
                <div>
                  <p className="text-xs text-white/70 mb-1">Volume</p>
                  <p className="text-lg font-semibold text-white">{stockData.volume}</p>
                </div>
              </div>
            </div>

            {/* Summary Card */}
            <div className="bg-card border border-border rounded-lg p-5">
              <h3 className="text-lg font-semibold mb-3">Key Metrics:</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-white/70">P/E Ratio</span>
                  <span className="font-medium">{stockData.peRatio}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/70">Dividend Yield</span>
                  <span className="font-medium">{stockData.dividend}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/70">Market Cap</span>
                  <span className="font-medium">{stockData.marketCap}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/70">Daily Volume</span>
                  <span className="font-medium">{stockData.volume}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-12 gap-4">
            {/* Chart Section */}
            <div className="col-span-5 bg-card border border-border rounded-lg p-4">
              {/* Chart Controls */}
              <div className="flex items-center gap-2 mb-3 flex-wrap">
                <button className="text-xs border border-primary text-primary px-2 py-1 rounded">1D</button>
                <button className="text-xs border border-gray-600 text-white/70 px-2 py-1 rounded hover:border-primary hover:text-primary">
                  1W
                </button>
                <button className="text-xs bg-primary text-white px-2 py-1 rounded">1M</button>
                <button className="text-xs border border-gray-600 text-white/70 px-2 py-1 rounded hover:border-primary hover:text-primary">
                  1Y
                </button>
                <button className="text-xs bg-primary text-white px-3 py-1 rounded">Volume</button>
                <button className="text-xs border border-gray-600 text-white/70 px-2 py-1 rounded hover:border-primary hover:text-primary">
                  60 DMA
                </button>
                <button className="text-xs border border-gray-600 text-white/70 px-2 py-1 rounded hover:border-primary hover:text-primary">
                  Fx +
                </button>
                <button className="text-white/70 hover:text-primary ml-auto">
                  <ChevronRight size={20} />
                </button>
              </div>

              {/* Chart Placeholder */}
              <div className="relative h-64 border border-border rounded">
                <CandlestickChart />
              </div>
            </div>

            {/* Sentiment Analysis Section */}
            <div className="col-span-4 bg-card border border-border rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold">Sentiment Analysis</h3>
                <ChevronRight size={20} className="text-white/70" />
              </div>
              <p className="text-xs text-white/70 mb-2">Sentiment Score</p>
              <div className="h-16 flex items-center justify-center mb-4">
                <div className="w-full bg-card rounded-full h-2">
                  <div className="bg-primary h-2 rounded-full" style={{ width: "60%" }}></div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="bg-background border border-border rounded-lg p-3 flex flex-col items-center justify-center h-24">
                  <p className="text-xs font-medium">Donut Graph</p>
                  <p className="text-xs font-medium">Here</p>
                </div>
                <div className="bg-background border border-border rounded-lg p-3 flex items-center justify-center h-24">
                  <p className="text-xs font-medium text-white/70">Reasoning</p>
                </div>
              </div>
            </div>

            {/* Technical/Fundamentals Section */}
            <div className="col-span-3 bg-card border border-border rounded-lg p-4">
              <div className="flex gap-2 mb-3 border-b border-border">
                <button className="pb-2 px-2 text-xs text-primary border-b-2 border-primary font-medium">
                  Technical
                </button>
                <button className="pb-2 px-2 text-xs text-white/70 hover:text-primary font-medium">
                  Fundamentals
                </button>
              </div>
              <div className="text-xs space-y-1">
                <p className="font-medium">Company name</p>
                <p>• Sector, industry</p>
                <p>• Market cap</p>
                <p>• P/E ratio</p>
                <p>• EPS</p>
                <p>• Revenue</p>
                <p>• Debt/Equity</p>
                <p>• ROE</p>
                <p>• Next earnings</p>
              </div>
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-6">
            <h3 className="text-xl font-semibold mb-4">News and analytics</h3>
            <div className="grid grid-cols-3 gap-4">
              <NewsCard
                icon="📈"
                iconBg="bg-primary/80/20"
                title="Tech stocks rally on positive inflation data"
                time="5 hours ago"
                source="Reuters"
                summary="Summary of impact on stock"
              />
              <NewsCard
                icon="🏛️"
                iconBg="bg-primary/80/20"
                title="Oil prices surge as OPEC+ announces production cuts"
                time="5 hours ago"
                source="Bloomberg"
                summary="Summary of impact on stock"
              />
              <NewsCard
                icon="🏛️"
                iconBg="bg-primary/80/20"
                title="Federal Reserve hints at interest rate stability for Q3"
                time="8 hours ago"
                source="Wall Street Journal"
                summary="Summary of impact on stock"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Candlestick Chart Component
function CandlestickChart() {
  return (
    <div className="w-full h-full p-4 flex items-end gap-1">
      {[...Array(50)].map((_, i) => {
        const height = Math.random() * 80 + 20
        const isPositive = Math.random() > 0.5
        const volumeHeight = Math.random() * 30 + 10

        return (
          <div key={i} className="flex-1 flex flex-col items-center justify-end gap-1">
            {/* Candlestick */}
            <div
              className={clsx("w-full rounded-sm", isPositive ? "bg-primary" : "bg-red-500")}
              style={{ height: `${height}%` }}
            />
            {/* Volume bar */}
            <div
              className={clsx("w-full rounded-sm opacity-50", isPositive ? "bg-primary" : "bg-red-500")}
              style={{ height: `${volumeHeight}px` }}
            />
          </div>
        )
      })}
    </div>
  )
}

// News Card Component
interface NewsCardProps {
  icon: string
  iconBg: string
  title: string
  time: string
  source: string
  summary: string
}

function NewsCard({ icon, iconBg, title, time, source, summary }: NewsCardProps) {
  return (
    <motion.div
      className="bg-background border border-border rounded-lg p-4 hover:border-primary/50 transition-colors cursor-pointer"
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
    >
      <div className="flex gap-3 mb-3">
        <div className={clsx("w-12 h-12 rounded flex items-center justify-center text-2xl", iconBg)}>{icon}</div>
        <div className="flex-1">
          <h4 className="text-sm font-medium mb-1 line-clamp-2">{title}</h4>
          <p className="text-xs text-white/70">
            {time} · {source}
          </p>
        </div>
      </div>
      <p className="text-xs text-white/70">{summary}</p>
    </motion.div>
  )
}
