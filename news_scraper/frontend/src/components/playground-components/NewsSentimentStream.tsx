"use client"

import { motion } from "framer-motion"
import type React from "react"

interface NewsItem {
  headline: string
  source: string
  timestamp: string
  currencyPair: string
  sentimentScore: number
  matchPercentage: number
}

interface NewsSentimentStreamProps {
  newsItems: NewsItem[]
}

export const NewsSentimentStream: React.FC<NewsSentimentStreamProps> = ({
  newsItems,
}) => {
  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      <div className="bg-[#0f2424] rounded-2xl p-8 shadow-2xl">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-[#ffffff] text-2xl font-semibold mb-2">
            News Sentiment Stream
          </h2>
          <p className="text-[#a8a8a8] text-sm">
            Macro & News, Geopolitical, Credit events
          </p>
        </div>

        {/* News Items */}
        <div className="space-y-6">
          {newsItems.map((item, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="pb-6 border-b border-[#3f3f46] last:border-b-0"
            >
              {/* News Content */}
              <div className="mb-3">
                <h3 className="text-[#ffffff] text-lg font-medium mb-2">
                  {item.headline}
                </h3>
                <div className="flex items-center gap-2 text-sm text-[#a8a8a8] mb-3">
                  <span>Source: {item.source}</span>
                  <span>•</span>
                  <span>Timestamp: {item.timestamp}</span>
                </div>
                <div className="inline-block">
                  <span className="text-[#008080] text-sm font-medium px-3 py-1 bg-[#008080]/10 rounded">
                    {item.currencyPair}
                  </span>
                </div>
              </div>

              {/* Sentiment Bar */}
              <div className="mt-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[#a8a8a8] text-sm">Sentiment</span>
                  <span className="text-[#a8a8a8] text-sm">
                    {item.matchPercentage}% Match
                  </span>
                </div>
                <div className="relative w-full h-2 bg-[#3f3f46] rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${item.matchPercentage}%` }}
                    transition={{ delay: index * 0.1 + 0.2, duration: 0.6 }}
                    className={`h-full rounded-full ${
                      item.sentimentScore > 0 ? "bg-[#00b894]" : "bg-[#d63031]"
                    }`}
                  />
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
