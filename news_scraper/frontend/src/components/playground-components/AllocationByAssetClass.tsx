"use client"

import { motion } from "framer-motion"
import { cn } from "@/lib/utils"
import type React from "react"

export interface AssetClass {
  name: string
  percentage: number
  change: number
}

interface AllocationByAssetClassProps {
  title?: string
  subtitle?: string
  assetClasses: AssetClass[]
}

const getAsset = (assetClasses: AssetClass[], name: string): AssetClass | undefined =>
  assetClasses.find((a) => a.name === name)

const formatChange = (value: number): string =>
  `${value >= 0 ? "+" : ""}${value.toFixed(1)}%`

const formatPercent = (value: number): string => `${value}%`

const AllocationByAssetClass: React.FC<AllocationByAssetClassProps> = ({
  title = "Allocation by Asset Class",
  subtitle = "Portfolio Composition",
  assetClasses,
}) => {
  const equities = getAsset(assetClasses, "Equities")
  const bonds = getAsset(assetClasses, "Bonds")
  const commodities = getAsset(assetClasses, "Commodities")
  const crypto = getAsset(assetClasses, "Crypto")
  const fx = getAsset(assetClasses, "FX")

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-7xl mx-auto bg-slate-900 rounded-3xl p-8 shadow-2xl"
    >
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-white mb-2">{title}</h2>
        <p className="text-slate-400 text-lg">{subtitle}</p>
      </div>

      {/* Grid Layout */}
      <div className="grid grid-cols-12 grid-rows-6 gap-3 h-[500px]">
        {/* Equities - Large box, top left */}
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.1, duration: 0.4 }}
          className={cn(
            "col-span-7 row-span-4 rounded-2xl p-6 flex flex-col justify-between",
            "bg-gradient-to-br from-teal-500 to-teal-700",
          )}
        >
          <div className="text-white font-medium text-lg">
            {equities?.name ?? "Equities"}
          </div>
          <div className="flex flex-col items-center justify-center flex-1">
            <div className="text-white font-bold text-7xl">
              {equities ? formatPercent(equities.percentage) : "0%"}
            </div>
          </div>
          <div className="text-white/90 text-sm text-right font-medium">
            {equities ? formatChange(equities.change) : "+0.0%"}
          </div>
        </motion.div>

        {/* Bonds - Large box, top right */}
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.15, duration: 0.4 }}
          className={cn(
            "col-span-5 row-span-6 rounded-2xl p-6 flex flex-col justify-between",
            "bg-gradient-to-br from-teal-600 to-teal-800",
          )}
        >
          <div className="text-white font-medium text-lg">
            {bonds?.name ?? "Bonds"}
          </div>
          <div className="flex flex-col items-center justify-center flex-1">
            <div className="text-white font-bold text-7xl">
              {bonds ? formatPercent(bonds.percentage) : "0%"}
            </div>
          </div>
          <div className="text-white/90 text-sm text-right font-medium">
            {bonds ? formatChange(bonds.change) : "+0.0%"}
          </div>
        </motion.div>

        {/* Commodities - Medium box, bottom left */}
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.4 }}
          className={cn(
            "col-span-3 row-span-2 rounded-2xl p-4 flex flex-col justify-between",
            "bg-gradient-to-br from-amber-900 to-amber-950",
          )}
        >
          <div className="text-white font-medium text-sm">
            {commodities?.name ?? "Commodities"}
          </div>
          <div className="flex flex-col items-center justify-center flex-1">
            <div className="text-white font-bold text-4xl">
              {commodities ? formatPercent(commodities.percentage) : "0%"}
            </div>
          </div>
          <div className="text-white/90 text-xs text-right font-medium">
            {commodities ? formatChange(commodities.change) : "+0.0%"}
          </div>
        </motion.div>

        {/* Crypto - Medium box, bottom center */}
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.25, duration: 0.4 }}
          className={cn(
            "col-span-2 row-span-2 rounded-2xl p-4 flex flex-col justify-between",
            "bg-gradient-to-br from-red-800 to-red-950",
          )}
        >
          <div className="text-white font-medium text-sm">
            {crypto?.name ?? "Crypto"}
          </div>
          <div className="flex flex-col items-center justify-center flex-1">
            <div className="text-white font-bold text-4xl">
              {crypto ? formatPercent(crypto.percentage) : "0%"}
            </div>
          </div>
          <div className="text-white/90 text-xs text-right font-medium">
            {crypto ? formatChange(crypto.change) : "+0.0%"}
          </div>
        </motion.div>

        {/* FX - Small box, bottom right */}
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.4 }}
          className={cn(
            "col-span-2 row-span-2 rounded-2xl p-4 flex flex-col justify-between",
            "bg-gradient-to-br from-teal-700 to-teal-900",
          )}
        >
          <div className="text-white font-medium text-sm">
            {fx?.name ?? "FX"}
          </div>
          <div className="flex flex-col items-center justify-center flex-1">
            <div className="text-white font-bold text-4xl">
              {fx ? formatPercent(fx.percentage) : "0%"}
            </div>
          </div>
          <div className="text-white/90 text-xs text-right font-medium">
            {fx ? formatChange(fx.change) : "+0.0%"}
          </div>
        </motion.div>
      </div>
    </motion.div>
  )
}

export default AllocationByAssetClass
