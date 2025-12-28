"use client"

import { motion } from "framer-motion"
import { SlidersHorizontal, RefreshCw } from "lucide-react"

export interface Trade {
  id: string
  time: string
  symbol: string
  action: "BUY" | "SELL"
  qty: number
  price: number
  profitLoss: number
}

export interface TradeLogProps {
  title?: string
  subtitle?: string
  trades: Trade[]
}

function TradeRow({ trade }: { trade: Trade }) {
  const isProfit = trade.profitLoss >= 0
  const plColor = isProfit ? "text-profit" : "text-loss"

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
      className="grid grid-cols-6 gap-4 border-b border-border px-6 py-5 transition-colors hover:bg-card-hover"
    >
      <div className="text-sm text-muted-foreground">{trade.time}</div>
      <div className="text-base font-bold text-foreground">{trade.symbol}</div>
      <div className="text-sm text-muted-foreground uppercase">{trade.action}</div>
      <div className="text-sm text-muted-foreground">{trade.qty}</div>
      <div className="text-sm text-muted-foreground">${trade.price.toFixed(2)}</div>
      <div className={`text-sm font-semibold ${plColor}`}>
        {isProfit ? "+" : "-"}${Math.abs(trade.profitLoss).toFixed(2)}
      </div>
    </motion.div>
  )
}

function TradeLogTable({ trades }: { trades: Trade[] }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="overflow-hidden rounded-2xl bg-card shadow-lg"
    >
      {/* Table Header */}
      <div className="grid grid-cols-6 gap-4 border-b border-border bg-card px-6 py-4">
        <div className="text-sm font-semibold text-foreground">Time</div>
        <div className="text-sm font-semibold text-foreground">Symbol</div>
        <div className="text-sm font-semibold text-foreground">Action</div>
        <div className="text-sm font-semibold text-foreground">Qty</div>
        <div className="text-sm font-semibold text-foreground">Price</div>
        <div className="text-sm font-semibold text-foreground">P/L</div>
      </div>

      {/* Table Rows */}
      <div>
        {trades.map((trade) => (
          <TradeRow key={trade.id} trade={trade} />
        ))}
      </div>
    </motion.div>
  )
}

export function TradeLog({
  title = "Trade Log",
  subtitle = "Historical Trades",
  trades,
}: TradeLogProps) {
  return (
    <div className="min-h-screen bg-background p-4 md:p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mx-auto max-w-7xl"
      >
        {/* Header */}
        <div className="mb-8 flex items-start justify-between">
          <div>
            <h1 className="text-4xl font-bold text-foreground">{title}</h1>
            <p className="mt-2 text-lg text-muted-foreground">{subtitle}</p>
          </div>

          <div className="flex items-center gap-3">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="rounded-lg bg-card p-3 text-foreground transition-colors hover:bg-card-hover"
              aria-label="Filter trades"
            >
              <SlidersHorizontal className="h-5 w-5" />
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05, rotate: 180 }}
              whileTap={{ scale: 0.95 }}
              transition={{ duration: 0.3 }}
              className="rounded-lg bg-card p-3 text-foreground transition-colors hover:bg-card-hover"
              aria-label="Refresh trades"
            >
              <RefreshCw className="h-5 w-5" />
            </motion.button>
          </div>
        </div>

        {/* Trade Log Table */}
        <TradeLogTable trades={trades} />
      </motion.div>
    </div>
  )
}
