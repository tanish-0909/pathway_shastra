"use client"

import type React from "react"

import { useState } from "react"
import type { TrendingTopic } from "../data/news"
import { TrendingUp, TrendingDown } from "lucide-react"

interface TrendingTopicsProps {
  topics: TrendingTopic[]
  onTopicClick?: (topic: TrendingTopic) => void
  onFollow?: (topic: TrendingTopic) => void
}

export function TrendingTopics({ topics, onTopicClick, onFollow }: TrendingTopicsProps) {
  const [followedTopics, setFollowedTopics] = useState<Set<string>>(new Set())
  const [hoveredTopic, setHoveredTopic] = useState<string | null>(null)

  const handleFollow = (e: React.MouseEvent, topic: TrendingTopic) => {
    e.stopPropagation()
    const newFollowed = new Set(followedTopics)
    if (newFollowed.has(topic.id)) {
      newFollowed.delete(topic.id)
    } else {
      newFollowed.add(topic.id)
    }
    setFollowedTopics(newFollowed)
    onFollow?.(topic)
  }

  return (
    <div className="bg-card rounded-xl p-4 border border-border">
      <h3 className="text-white font-semibold text-lg mb-4">Trending Topics</h3>
      <div className="space-y-2">
        {topics.map((topic) => (
          <div
            key={topic.id}
            className={`flex items-center gap-3 p-2 rounded-lg cursor-pointer transition-all duration-200
              ${hoveredTopic === topic.id ? "bg-white/5" : ""}`}
            onMouseEnter={() => setHoveredTopic(topic.id)}
            onMouseLeave={() => setHoveredTopic(null)}
            onClick={() => onTopicClick?.(topic)}
          >
            {/* Company/Sector Icon */}
            {topic.icon && (
              <span className="text-lg" role="img" aria-label={topic.label}>
                {topic.icon}
              </span>
            )}
            <div className={`transition-transform duration-200 ${hoveredTopic === topic.id ? "scale-125" : ""}`}>
              {topic.trend === "up" ? (
                <TrendingUp className="w-5 h-5 text-primary" />
              ) : (
                <TrendingDown className="w-5 h-5 text-red-400" />
              )}
            </div>
            <span className="text-white flex-1">{topic.label}</span>
            {/* Mention count badge */}
            {topic.count !== undefined && (
              <span className="text-xs text-white/70 bg-white/10 px-2 py-0.5 rounded-full">
                {topic.count} mentions
              </span>
            )}
            <button
              onClick={(e) => handleFollow(e, topic)}
              className={`p-1 rounded-full transition-all duration-200 ${
                followedTopics.has(topic.id)
                  ? "bg-primary text-white rotate-45"
                  : hoveredTopic === topic.id
                    ? "bg-white/10 text-white/70 opacity-100"
                    : "opacity-0"
              }`}
            >
              {/* <Plus className="w-4 h-4" /> */}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
