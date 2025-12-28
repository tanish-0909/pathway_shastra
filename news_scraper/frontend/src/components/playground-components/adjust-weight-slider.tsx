"use client"

import type React from "react"

import { useState, useCallback } from "react"

interface AdjustWeightSliderProps {
  title?: string
  label?: string
  initialValue?: number
  min?: number
  max?: number
  onChange?: (value: number) => void
}

export function AdjustWeightSlider({
  title = "Adjust Weight",
  label = "Target Allocation (%)",
  initialValue = 45,
  min = 0,
  max = 100,
  onChange,
}: AdjustWeightSliderProps) {
  const [value, setValue] = useState(initialValue)
  const [inputValue, setInputValue] = useState(initialValue.toString())

  const handleSliderChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = Number(e.target.value)
      setValue(newValue)
      setInputValue(newValue.toString())
      onChange?.(newValue)
    },
    [onChange],
  )

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const raw = e.target.value.replace(/[^0-9]/g, "")
      setInputValue(raw)

      const parsed = Number(raw)
      if (!isNaN(parsed) && parsed >= min && parsed <= max) {
        setValue(parsed)
        onChange?.(parsed)
      }
    },
    [min, max, onChange],
  )

  const handleInputBlur = useCallback(() => {
    let parsed = Number(inputValue)
    if (isNaN(parsed)) parsed = min
    if (parsed < min) parsed = min
    if (parsed > max) parsed = max
    setValue(parsed)
    setInputValue(parsed.toString())
    onChange?.(parsed)
  }, [inputValue, min, max, onChange])

  const percentage = ((value - min) / (max - min)) * 100

  return (
    <div className="rounded-2xl p-6" style={{ backgroundColor: "#0d2a2b" }}>
      <h2 className="text-xl font-bold text-white mb-6">{title}</h2>

      <div className="space-y-3">
        <label className="text-gray-300 text-sm">{label}</label>

        <div className="flex items-center gap-4">
          {/* Slider container */}
          <div className="flex-1 relative">
            {/* Custom track background */}
            <div className="relative h-2 rounded-full overflow-hidden" style={{ backgroundColor: "#3d4f4f" }}>
              {/* Filled portion */}
              <div
                className="absolute top-0 left-0 h-full rounded-full"
                style={{
                  width: `${percentage}%`,
                  backgroundColor: "#2dd4bf",
                }}
              />
            </div>

            {/* Native range input (invisible but functional) */}
            <input
              type="range"
              min={min}
              max={max}
              value={value}
              onChange={handleSliderChange}
              className="absolute top-1/2 left-0 w-full -translate-y-1/2 appearance-none bg-transparent cursor-pointer"
              style={{
                height: "20px",
              }}
            />

            {/* Custom thumb */}
            <div
              className="absolute top-1/2 -translate-y-1/2 pointer-events-none"
              style={{
                left: `calc(${percentage}% - 10px)`,
              }}
            >
              <div
                className="w-5 h-5 rounded-full bg-white shadow-lg"
                style={{
                  boxShadow: "0 2px 8px rgba(0, 0, 0, 0.3)",
                }}
              />
            </div>

            {/* Min/Max labels */}
            <div className="flex justify-between mt-2">
              <span className="text-gray-400 text-sm">{min}%</span>
              <span className="text-gray-400 text-sm">{max}%</span>
            </div>
          </div>

          {/* Value input box */}
          <div
            className="flex items-center gap-1 px-4 py-2 rounded-lg border"
            style={{
              backgroundColor: "#1a3a3b",
              borderColor: "#2dd4bf",
            }}
          >
            <input
              type="text"
              value={inputValue}
              onChange={handleInputChange}
              onBlur={handleInputBlur}
              className="w-10 bg-transparent text-white text-lg font-medium text-right outline-none"
            />
            <span className="text-gray-400 text-lg">%</span>
          </div>
        </div>
      </div>

      <style jsx>{`
        input[type="range"]::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 20px;
          height: 20px;
          background: transparent;
          cursor: pointer;
        }
        input[type="range"]::-moz-range-thumb {
          width: 20px;
          height: 20px;
          background: transparent;
          border: none;
          cursor: pointer;
        }
      `}</style>
    </div>
  )
}
