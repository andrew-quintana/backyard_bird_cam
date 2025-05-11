"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"

interface CustomDateSliderProps {
  startDate: Date
  endDate: Date
  minDate: Date
  maxDate: Date
  onChange: (startDate: Date, endDate: Date) => void
}

export function CustomDateSlider({ startDate, endDate, minDate, maxDate, onChange }: CustomDateSliderProps) {
  const sliderRef = useRef<HTMLDivElement>(null)
  const [isDragging, setIsDragging] = useState<"left" | "right" | null>(null)
  const [leftPos, setLeftPos] = useState(0)
  const [rightPos, setRightPos] = useState(100)

  // Calculate positions based on dates
  useEffect(() => {
    const totalRange = maxDate.getTime() - minDate.getTime()
    const leftOffset = ((startDate.getTime() - minDate.getTime()) / totalRange) * 100
    const rightOffset = ((endDate.getTime() - minDate.getTime()) / totalRange) * 100

    setLeftPos(leftOffset)
    setRightPos(rightOffset)
  }, [startDate, endDate, minDate, maxDate])

  // Format date as MMM D, YYYY
  const formatDate = (date: Date) => {
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    })
  }

  // Handle mouse down on handles
  const handleMouseDown = (e: React.MouseEvent, handle: "left" | "right") => {
    e.preventDefault()
    setIsDragging(handle)
  }

  // Handle mouse move
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging || !sliderRef.current) return

      const rect = sliderRef.current.getBoundingClientRect()
      const position = ((e.clientX - rect.left) / rect.width) * 100

      if (isDragging === "left") {
        if (position < rightPos && position >= 0) {
          setLeftPos(Math.max(0, Math.min(position, 100)))

          // Calculate new date
          const totalRange = maxDate.getTime() - minDate.getTime()
          const newTime = minDate.getTime() + (totalRange * position) / 100
          const newDate = new Date(newTime)

          onChange(newDate, endDate)
        }
      } else {
        if (position > leftPos && position <= 100) {
          setRightPos(Math.max(0, Math.min(position, 100)))

          // Calculate new date
          const totalRange = maxDate.getTime() - minDate.getTime()
          const newTime = minDate.getTime() + (totalRange * position) / 100
          const newDate = new Date(newTime)

          onChange(startDate, newDate)
        }
      }
    }

    const handleMouseUp = () => {
      setIsDragging(null)
    }

    if (isDragging) {
      document.addEventListener("mousemove", handleMouseMove)
      document.addEventListener("mouseup", handleMouseUp)
    }

    return () => {
      document.removeEventListener("mousemove", handleMouseMove)
      document.removeEventListener("mouseup", handleMouseUp)
    }
  }, [isDragging, leftPos, rightPos, onChange, startDate, endDate, minDate, maxDate])

  return (
    <div className="space-y-6">
      {/* Date headers */}
      <div className="flex justify-between items-center">
        <div>
          <span className="text-sm font-medium text-[#558b2f]">From</span>
          <p className="text-lg font-semibold text-[#33691e]">{formatDate(startDate)}</p>
        </div>
        <div className="text-right">
          <span className="text-sm font-medium text-[#558b2f]">To</span>
          <p className="text-lg font-semibold text-[#33691e]">{formatDate(endDate)}</p>
        </div>
      </div>

      {/* Slider */}
      <div className="relative h-8" ref={sliderRef}>
        {/* Slider track */}
        <div className="absolute top-1/2 left-0 right-0 h-2 -mt-1 rounded-full overflow-hidden">
          {/* Black background */}
          <div className="absolute inset-0 bg-black/10"></div>

          {/* Green active area */}
          <div
            className="absolute inset-y-0 bg-[#8bc34a]"
            style={{
              left: `${leftPos}%`,
              right: `${100 - rightPos}%`,
            }}
          ></div>
        </div>

        {/* Left handle */}
        <div
          className="absolute top-1/2 -mt-3 w-6 h-6 bg-white border-2 border-[#8bc34a] rounded-full shadow-md cursor-pointer z-10"
          style={{ left: `calc(${leftPos}% - 12px)` }}
          onMouseDown={(e) => handleMouseDown(e, "left")}
        >
          <div className="absolute inset-0 m-0.5 bg-[#8bc34a] rounded-full"></div>
        </div>

        {/* Right handle */}
        <div
          className="absolute top-1/2 -mt-3 w-6 h-6 bg-white border-2 border-[#8bc34a] rounded-full shadow-md cursor-pointer z-10"
          style={{ left: `calc(${rightPos}% - 12px)` }}
          onMouseDown={(e) => handleMouseDown(e, "right")}
        >
          <div className="absolute inset-0 m-0.5 bg-[#8bc34a] rounded-full"></div>
        </div>
      </div>

      {/* Date labels */}
      <div className="flex justify-between items-center">
        <div className="text-xs text-[#558b2f]">{formatDate(minDate)}</div>
        <div className="text-xs text-[#558b2f]">{formatDate(maxDate)}</div>
      </div>

      {/* Summary */}
      <div className="pt-4 border-t border-[#e0f2f1]">
        <p className="text-sm text-[#7cb342]">
          Showing birds from <span className="font-medium text-[#33691e]">{formatDate(startDate)}</span> to{" "}
          <span className="font-medium text-[#33691e]">{formatDate(endDate)}</span>
        </p>
      </div>
    </div>
  )
}
