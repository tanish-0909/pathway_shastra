"use client"

import { useState, useRef } from "react"
import type { DailyBriefing as DailyBriefingType } from "../data/news"
import { Play, Pause, Volume2, VolumeX, Loader2, AlertCircle } from "lucide-react"

interface DailyBriefingProps {
  briefing: DailyBriefingType
  videoUrl?: string | null
  videoStatus?: "pending" | "generating" | "completed" | "failed"
  onPlay?: () => void
}

export function DailyBriefing({ briefing, videoUrl, videoStatus = "completed", onPlay }: DailyBriefingProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [isHovered, setIsHovered] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [showVideo, setShowVideo] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)

  const handlePlay = () => {
    if (videoUrl && videoStatus === "completed") {
      setShowVideo(true)
      setIsPlaying(true)
      setTimeout(() => {
        videoRef.current?.play()
      }, 100)
    }
    onPlay?.()
  }

  const handleVideoClick = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause()
      } else {
        videoRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }

  const handleMuteToggle = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (videoRef.current) {
      videoRef.current.muted = !isMuted
      setIsMuted(!isMuted)
    }
  }

  const handleVideoEnd = () => {
    setIsPlaying(false)
    setShowVideo(false)
  }

  const isLoading = videoStatus === "generating" || videoStatus === "pending"
  const hasFailed = videoStatus === "failed"
  const canPlay = videoUrl && videoStatus === "completed"

  return (
    <div
      className={`relative rounded-xl overflow-hidden cursor-pointer transition-all duration-300
        ${isHovered ? "shadow-xl shadow-primary/20 scale-[1.02]" : ""}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={showVideo ? handleVideoClick : handlePlay}
    >
      {/* Video Player */}
      {showVideo && videoUrl && (
        <video
          ref={videoRef}
          src={videoUrl}
          className="w-full h-44 object-cover"
          onEnded={handleVideoEnd}
          onPause={() => setIsPlaying(false)}
          onPlay={() => setIsPlaying(true)}
        />
      )}

      {/* Thumbnail (shown when video is not playing) */}
      {!showVideo && (
        <>
          <img
            src={briefing.thumbnailUrl || "/placeholder.svg"}
            alt={briefing.title}
            className={`w-full h-44 object-cover transition-transform duration-700 ${isHovered ? "scale-110" : ""}`}
          />
          <div
            className={`absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent transition-opacity duration-300 ${isHovered ? "opacity-90" : ""}`}
          />
        </>
      )}

      {/* Play/Pause Button */}
      <div className="absolute inset-0 flex items-center justify-center">
        {isLoading ? (
          <div className="w-14 h-14 bg-white/10 rounded-full flex items-center justify-center">
            <Loader2 className="w-6 h-6 text-white animate-spin" />
          </div>
        ) : hasFailed ? (
          <div className="w-14 h-14 bg-red-700 rounded-full flex items-center justify-center">
            <AlertCircle className="w-6 h-6 text-white" />
          </div>
        ) : (
          <button
            className={`w-14 h-14 bg-primary rounded-full flex items-center justify-center transition-all duration-300
              ${isPlaying ? "bg-primary/80 scale-90 opacity-0 hover:opacity-100" : "hover:bg-primary/80 hover:scale-110"}
              ${!canPlay ? "bg-white/20 cursor-not-allowed" : ""}`}
            disabled={!canPlay}
          >
            {isPlaying ? (
              <Pause className="w-6 h-6 text-white fill-white" />
            ) : (
              <Play className="w-6 h-6 text-white fill-white ml-1" />
            )}
          </button>
        )}
      </div>

      {/* Volume Control (shown when video is playing) */}
      <div
        className={`absolute top-3 right-3 p-2 rounded-full bg-black/50 transition-all duration-300 ${
          isHovered || showVideo ? "opacity-100 translate-y-0" : "opacity-0 -translate-y-2"
        }`}
        onClick={handleMuteToggle}
      >
        {isMuted ? (
          <VolumeX className="w-4 h-4 text-white" />
        ) : (
          <Volume2 className="w-4 h-4 text-white" />
        )}
      </div>

      {/* Status Badge */}
      {isLoading && (
        <div className="absolute top-3 left-3 px-2 py-1 rounded-full bg-yellow-500/80 text-xs text-white font-medium">
          Generating...
        </div>
      )}
      {hasFailed && (
        <div className="absolute top-3 left-3 px-2 py-1 rounded-full bg-red-500/80 text-xs text-white font-medium">
          Generation failed
        </div>
      )}

      {/* Title/Subtitle */}
      <div className={`absolute bottom-0 left-0 right-0 p-4 ${showVideo ? "bg-gradient-to-t from-black/80 to-transparent" : ""}`}>
        <h3 className="text-white font-semibold">{briefing.title}</h3>
        <p className="text-white/70 text-sm">{briefing.subtitle}</p>
      </div>
    </div>
  )
}
