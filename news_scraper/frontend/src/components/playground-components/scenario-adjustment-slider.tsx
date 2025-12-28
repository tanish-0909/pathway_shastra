"use client"

import type React from "react"

import { useState, useCallback } from "react"

interface ScenarioAdjustmentData {
  label: string
  description: string
  value: number
  min: number
  max: number
  unit: string
}

interface ScenarioAdjustmentSliderProps {
  data: ScenarioAdjustmentData
  title?: string
  onChange?: (value: number) => void
}

export function ScenarioAdjustmentSlider({
  data,
  title = "Scenario Adjustment",
  onChange,
}: ScenarioAdjustmentSliderProps) {
  const [value, setValue] = useState(data.value)

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = Number.parseInt(e.target.value, 10)
      setValue(newValue)
      onChange?.(newValue)
    },
    [onChange],
  )

  const formatValue = (val: number): string => {
    if (val > 0) return `+${val} ${data.unit}`
    if (val < 0) return `${val} ${data.unit}`
    return `0 ${data.unit}`
  }

  // Calculate the percentage for the gradient (centered at 0)
  const range = data.max - data.min
  const zeroPosition = ((0 - data.min) / range) * 100
  const valuePosition = ((value - data.min) / range) * 100

  // Determine gradient based on value position relative to zero
  const getTrackGradient = () => {
    if (value >= 0) {
      // Value is at or above zero - teal from min to value
      return `linear-gradient(to right, 
        #2dd4bf 0%, 
        #2dd4bf ${valuePosition}%, 
        #374151 ${valuePosition}%, 
        #374151 100%)`
    } else {
      // Value is below zero - teal from value to zero, gray elsewhere
      return `linear-gradient(to right, 
        #374151 0%, 
        #374151 ${valuePosition}%, 
        #2dd4bf ${valuePosition}%, 
        #2dd4bf ${zeroPosition}%,
        #374151 ${zeroPosition}%, 
        #374151 100%)`
    }
  }

  return (
    <div className="bg-[#0d2a2d] rounded-2xl p-6 border border-[#1a4a4f]">
      {/* Header */}
      <h2 className="text-white text-2xl font-bold mb-2">{title}</h2>
      <p className="text-gray-400 text-sm mb-8">{data.description}</p>

      {/* Slider Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-white font-medium">{data.label}</span>
          <div className="bg-[#1e3a3e] border border-[#2a5a5e] rounded-lg px-4 py-2 min-w-[100px] text-center">
            <span className="text-white text-lg font-medium">{formatValue(value)}</span>
          </div>
        </div>

        {/* Custom Slider */}
        <div className="relative pt-2 pb-1">
          <input
            type="range"
            min={data.min}
            max={data.max}
            value={value}
            onChange={handleChange}
            className="w-full h-1 rounded-full appearance-none cursor-pointer slider-scenario"
            style={{
              background: getTrackGradient(),
            }}
          />

          {/* Tick marks */}
          <div className="absolute top-2 left-0 right-0 h-1 pointer-events-none">
            {/* Min tick */}
            <div className="absolute w-0.5 h-3 bg-gray-500 -top-1" style={{ left: "0%" }} />
            {/* Center tick (0) */}
            <div
              className="absolute w-0.5 h-3 bg-gray-500 -top-1"
              style={{ left: `${zeroPosition}%`, transform: "translateX(-50%)" }}
            />
            {/* Max tick */}
            <div className="absolute w-0.5 h-3 bg-gray-500 -top-1" style={{ right: "0%" }} />
          </div>
        </div>

        {/* Labels */}
        <div className="flex justify-between text-gray-400 text-sm">
          <span>Min</span>
          <span style={{ marginLeft: `${zeroPosition - 50}%` }}>0</span>
          <span>Max</span>
        </div>
      </div>

      <style jsx>{`
        .slider-scenario::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: white;
          cursor: pointer;
          border: 2px solid #2dd4bf;
          box-shadow: 0 0 10px rgba(45, 212, 191, 0.3);
          transition: box-shadow 0.2s ease;
        }

        .slider-scenario::-webkit-slider-thumb:hover {
          box-shadow: 0 0 15px rgba(45, 212, 191, 0.5);
        }

        .slider-scenario::-moz-range-thumb {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: white;
          cursor: pointer;
          border: 2px solid #2dd4bf;
          box-shadow: 0 0 10px rgba(45, 212, 191, 0.3);
          transition: box-shadow 0.2s ease;
        }

        .slider-scenario::-moz-range-thumb:hover {
          box-shadow: 0 0 15px rgba(45, 212, 191, 0.5);
        }
      `}</style>
    </div>
  )
}
