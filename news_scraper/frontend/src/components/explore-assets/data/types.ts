export interface MarketIndex {
  id: string
  name: string
  value: number
  change: number
  changePercent: number
  trend: "up" | "down"
  chartData: number[]
}

export interface Asset {
  id: string
  name: string
  ticker: string
  assetType: "bonds" | "stocks" | "etfs" | "commodities"
  // Bond specific
  priceOfPar?: number
  yieldToMaturity?: string
  coupon?: string
  maturityDate?: string
  duration?: number
  changeBps?: number
  // Stock specific
  price?: number
  change?: number
  changePercent?: number
  marketCap?: string
  peRatio?: number
  dividend?: string
  volume?: string
  // ETF specific
  nav?: number
  expenseRatio?: string
  aum?: string
  holdings?: number
  // Gold specific
  pricePerOz?: number
  purity?: string
  weight?: string
  premium?: number
  // Common
  isHeld: boolean
  region: string
  sector: string
}

export interface FilterOption {
  label: string
  value: string
}
