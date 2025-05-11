"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { Checkbox } from "@/components/ui/checkbox"
import { Button } from "@/components/ui/button"
import { Download, Tag, X, ChevronLeft, Calendar } from "lucide-react"
import Image from "next/image"
import { cn } from "@/lib/utils"
import LandingPage from "./landing-page"
import { getResults, getImageUrl } from "@/lib/api"

// Sample data for bird types
const birdTypes = [
  { id: "sparrow", label: "Sparrow" },
  { id: "robin", label: "Robin" },
  { id: "bluebird", label: "Bluebird" },
  { id: "cardinal", label: "Cardinal" },
  { id: "finch", label: "Finch" },
  { id: "hummingbird", label: "Hummingbird" },
  { id: "chickadee", label: "Chickadee" },
  { id: "warbler", label: "Warbler" },
]

// Sample data for images
const generateImages = () => {
  const images = []
  const now = new Date()

  for (let i = 1; i <= 12; i++) {
    const date = new Date(now)
    date.setDate(date.getDate() - Math.floor(Math.random() * 60))

    images.push({
      id: i,
      src: `/placeholder.svg?height=400&width=600`,
      alt: `Bird image ${i}`,
      date: date,
      type: birdTypes[Math.floor(Math.random() * birdTypes.length)].id,
      location: "Springtime Park",
    })
  }

  return images.sort((a, b) => b.date.getTime() - a.date.getTime())
}

// Helper function to format date as MMM DD, YYYY
const formatDateShort = (date: Date) => {
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  })
}

export default function BirdGallery() {
  const [images, setImages] = useState<any[]>([])
  const [selectedFilters, setSelectedFilters] = useState<string[]>([])
  const [selectedImages, setSelectedImages] = useState<number[]>([])
  const [activeImage, setActiveImage] = useState<any | null>(null)
  const [showLandingPage, setShowLandingPage] = useState(false)
  const mainContentRef = useRef<HTMLDivElement>(null)
  const sliderRef = useRef<HTMLDivElement>(null)
  const [scrollPosition, setScrollPosition] = useState(0)
  const [isDragging, setIsDragging] = useState<"left" | "right" | null>(null)

  // Get current date and date 60 days ago
  const today = new Date()
  const sixtyDaysAgo = new Date(today)
  sixtyDaysAgo.setDate(today.getDate() - 60)

  // State for selected dates - using specific dates from the example
  const [startDate, setStartDate] = useState(new Date(2025, 3, 1)) // Apr 1, 2025
  const [endDate, setEndDate] = useState(new Date(2025, 3, 18)) // Apr 18, 2025

  // Calculate positions for the slider
  const totalRange = today.getTime() - sixtyDaysAgo.getTime()
  const leftPos = ((startDate.getTime() - sixtyDaysAgo.getTime()) / totalRange) * 100
  const rightPos = ((endDate.getTime() - sixtyDaysAgo.getTime()) / totalRange) * 100

  useEffect(() => {
    // Fetch real data from the API
    const fetchData = async () => {
      try {
        const data = await getResults({
          limit: 50, // Get a reasonable number of results
          birdOnly: true // Only show detections with birds
        });
        
        if (data.success && data.results) {
          // Transform API data to match our component's expected format
          const formattedImages = data.results.map(result => {
            // Parse the date from the timestamp
            const date = new Date(result.timestamp);
            
            // Find the matching bird type
            const typeId = result.species.toLowerCase().includes('cardinal') ? 'cardinal' :
                          result.species.toLowerCase().includes('robin') ? 'robin' :
                          result.species.toLowerCase().includes('blue') ? 'bluebird' :
                          result.species.toLowerCase().includes('finch') ? 'finch' :
                          result.species.toLowerCase().includes('chickadee') ? 'chickadee' :
                          result.species.toLowerCase().includes('warbler') ? 'warbler' :
                          result.species.toLowerCase().includes('hummingbird') ? 'hummingbird' :
                          'sparrow'; // Default
            
            return {
              id: result.id,
              src: result.annotated_path || result.image_path,
              alt: `Bird image - ${result.species || 'Unknown species'}`,
              date: date,
              type: typeId,
              location: "Birdhouse Camera",
              species: result.species || "Unknown species",
              confidence: result.confidence || 0
            };
          });
          
          // Sort by date (newest first)
          const sortedImages = formattedImages.sort((a, b) => b.date.getTime() - a.date.getTime());
          setImages(sortedImages);
        }
      } catch (error) {
        console.error("Error fetching bird data:", error);
        // Fallback to mock data
        setImages(generateImages());
      }
    };

    fetchData();

    const handleScroll = () => {
      if (mainContentRef.current) {
        setScrollPosition(window.scrollY);
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Handle mouse down on handles
  const handleMouseDown = (e: React.MouseEvent, handle: "left" | "right") => {
    e.preventDefault()
    setIsDragging(handle)
  }

  // Handle mouse move for dragging
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging || !sliderRef.current) return

      const rect = sliderRef.current.getBoundingClientRect()
      const position = ((e.clientX - rect.left) / rect.width) * 100
      const totalRange = today.getTime() - sixtyDaysAgo.getTime()

      if (isDragging === "left") {
        if (position < rightPos && position >= 0) {
          const newTime = sixtyDaysAgo.getTime() + (totalRange * position) / 100
          const newDate = new Date(newTime)
          setStartDate(newDate)
        }
      } else {
        if (position > leftPos && position <= 100) {
          const newTime = sixtyDaysAgo.getTime() + (totalRange * position) / 100
          const newDate = new Date(newTime)
          setEndDate(newDate)
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
  }, [isDragging, leftPos, rightPos, sixtyDaysAgo, today])

  const toggleFilter = (id: string) => {
    setSelectedFilters((prev) => (prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]))
  }

  const toggleImageSelection = (id: number) => {
    setSelectedImages((prev) => (prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]))
  }

  const clearSelection = () => {
    setSelectedImages([])
  }

  const showImageDetails = (image: any) => {
    setActiveImage(image)
  }

  const closeImageDetails = () => {
    setActiveImage(null)
  }

  const filteredImages = images.filter((image) => {
    const dateInRange = image.date >= startDate && image.date <= endDate
    const typeMatches = selectedFilters.length === 0 || selectedFilters.includes(image.type)

    return dateInRange && typeMatches
  })

  const formatDate = (date: Date) => {
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    })
  }

  if (showLandingPage) {
    return <LandingPage />
  }

  // Calculate the top position for the sticky sidebar
  const sidebarTopPosition = Math.max(0, 16 - scrollPosition)
  const sidebarStyle = {
    top: `${sidebarTopPosition}px`,
    maxHeight: `calc(100vh - ${sidebarTopPosition}px)`,
  }

  return (
    <div className="flex min-h-screen">
      {/* Sticky Sidebar */}
      <div
        className="w-64 bg-white border-r border-[#d1e8cf] p-6 shadow-sm fixed left-0 overflow-auto transition-all duration-200 z-10"
        style={sidebarStyle}
      >
        <div className="mb-6">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowLandingPage(true)}
            className="text-[#558b2f] hover:text-[#33691e] hover:bg-[#f1f8e9] -ml-2 mb-2"
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Back to Home
          </Button>
          <h1 className="text-2xl font-bold text-[#2e7d32] mb-1">Birdhouse Camera Platform</h1>
          <p className="text-sm text-[#558b2f]">Filter your collection</p>
        </div>

        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-[#33691e]">Bird Types</h2>
          <div className="space-y-2">
            {birdTypes.map((type) => (
              <div key={type.id} className="flex items-center space-x-2">
                <Checkbox
                  id={type.id}
                  checked={selectedFilters.includes(type.id)}
                  onCheckedChange={() => toggleFilter(type.id)}
                  className="border-[#aed581] data-[state=checked]:bg-[#8bc34a] data-[state=checked]:text-white"
                />
                <label
                  htmlFor={type.id}
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  {type.label}
                </label>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-[#d1e8cf]">
          <p className="text-xs text-[#689f38] italic">Discover the beauty of spring through our bird collection</p>
          <div className="mt-4">
            <div className="h-24 w-full rounded-lg bg-[#f1f8e9] p-3 flex items-center justify-center">
              <div className="text-center">
                <p className="text-xs text-[#558b2f]">Found</p>
                <p className="text-2xl font-bold text-[#33691e]">{filteredImages.length}</p>
                <p className="text-xs text-[#558b2f]">birds</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content with left margin to account for fixed sidebar */}
      <div className="flex-1 p-6 ml-64" ref={mainContentRef}>
        {/* Selection Toolbar */}
        {selectedImages.length > 0 && (
          <div className="sticky top-0 bg-white shadow-md z-10 p-4 flex items-center justify-between border-b border-[#d1e8cf]">
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-[#558b2f]">
                {selectedImages.length} {selectedImages.length === 1 ? "image" : "images"} selected
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                className="text-[#558b2f] border-[#aed581] hover:bg-[#f1f8e9] hover:text-[#33691e]"
              >
                <Download className="h-4 w-4 mr-1" />
                Download
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="text-[#558b2f] border-[#aed581] hover:bg-[#f1f8e9] hover:text-[#33691e]"
              >
                <Tag className="h-4 w-4 mr-1" />
                Relabel
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={clearSelection}
                className="text-[#558b2f] hover:bg-[#f1f8e9] hover:text-[#33691e]"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}

        {/* Date Range Slider */}
        <div className={cn("mb-8", selectedImages.length > 0 ? "mt-16" : "")}>
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-lg font-semibold text-[#33691e]">Date Range</h2>
            <div className="flex items-center">
              <Calendar className="h-4 w-4 mr-1 text-[#558b2f]" />
              <span className="text-sm text-[#558b2f]">Select specific dates</span>
            </div>
          </div>

          <div className="bg-white rounded-xl p-5 border border-[#d1e8cf] shadow-sm">
            {/* Date headers */}
            <div className="flex justify-between items-center mb-6">
              <div>
                <span className="text-sm font-medium text-[#558b2f]">From</span>
                <p className="text-lg font-semibold text-[#33691e]">{formatDateShort(startDate)}</p>
              </div>
              <div className="text-right">
                <span className="text-sm font-medium text-[#558b2f]">To</span>
                <p className="text-lg font-semibold text-[#33691e]">{formatDateShort(endDate)}</p>
              </div>
            </div>

            {/* Custom slider */}
            <div className="relative h-12 mb-4" ref={sliderRef}>
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
            <div className="flex justify-between items-center mb-2">
              <div className="text-xs text-[#558b2f]">{formatDateShort(sixtyDaysAgo)}</div>
              <div className="text-xs text-[#558b2f]">{formatDateShort(today)}</div>
            </div>

            {/* Timeline labels */}
            <div className="flex justify-between">
              <span className="text-xs text-[#7cb342]">60 days ago</span>
              <span className="text-xs text-[#7cb342]">Today</span>
            </div>

            <div className="pt-4 border-t border-[#e0f2f1] mt-4">
              <p className="text-sm text-[#7cb342]">
                Showing birds from <span className="font-medium text-[#33691e]">{formatDateShort(startDate)}</span> to{" "}
                <span className="font-medium text-[#33691e]">{formatDateShort(endDate)}</span>
              </p>
            </div>
          </div>
        </div>

        {/* Bird Statistics */}
        <div className="mb-8 bg-[#f1f8e9] rounded-lg p-4 border border-[#d1e8cf]">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-4 md:mb-0">
              <h3 className="text-lg font-semibold text-[#33691e]">Bird Activity</h3>
              <p className="text-sm text-[#558b2f]">Welcome back, Momma! Here's what you've missed.</p>
            </div>
            <div className="flex space-x-6">
              <div className="text-center">
                <p className="text-3xl font-bold text-[#33691e]">14</p>
                <p className="text-xs text-[#558b2f]">Birds since last visit</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-[#33691e]">23</p>
                <p className="text-xs text-[#558b2f]">Total species visited</p>
              </div>
            </div>
          </div>
        </div>

        {/* Image Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredImages.map((image) => (
            <div
              key={image.id}
              className="relative group bg-white rounded-lg overflow-hidden shadow-sm border border-[#e0f2f1] hover:shadow-md transition-all duration-200"
            >
              <div className="absolute top-2 right-2 z-10">
                <Checkbox
                  checked={selectedImages.includes(image.id)}
                  onCheckedChange={() => toggleImageSelection(image.id)}
                  className="h-5 w-5 border-2 border-white bg-white/80 data-[state=checked]:bg-[#8bc34a] data-[state=checked]:text-white"
                />
              </div>
              <div className="cursor-pointer" onClick={() => showImageDetails(image)}>
                <div className="aspect-[4/3] relative">
                  <Image src={image.src || "/placeholder.svg"} alt={image.alt} fill className="object-cover" />
                </div>
                <div className="p-3">
                  <p className="text-sm font-medium text-[#33691e]">
                    {birdTypes.find((type) => type.id === image.type)?.label}
                  </p>
                  <p className="text-xs text-[#7cb342]">{formatDate(image.date)}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredImages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-64 bg-[#f1f8e9] rounded-lg border border-dashed border-[#aed581] p-6">
            <p className="text-lg font-medium text-[#558b2f]">No birds found</p>
            <p className="text-sm text-[#7cb342] mt-1">Try adjusting your filters</p>
          </div>
        )}
      </div>

      {/* Image Details Side Panel */}
      {activeImage && (
        <div className="fixed inset-0 bg-black/50 z-50 flex justify-end">
          <div className="w-full max-w-md bg-white h-full overflow-y-auto shadow-xl animate-in slide-in-from-right">
            <div className="sticky top-0 bg-white z-10 p-4 border-b border-[#d1e8cf] flex justify-between items-center">
              <h2 className="text-lg font-semibold text-[#33691e]">Image Details</h2>
              <Button variant="ghost" size="sm" onClick={closeImageDetails} className="text-[#558b2f]">
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="p-6">
              <div className="aspect-[4/3] relative mb-6">
                <Image
                  src={activeImage.src || "/placeholder.svg"}
                  alt={activeImage.alt}
                  fill
                  className="object-cover rounded-lg"
                />
              </div>

              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-medium text-[#7cb342]">Bird Type</h3>
                  <p className="text-lg font-semibold text-[#33691e]">
                    {birdTypes.find((type) => type.id === activeImage.type)?.label}
                  </p>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-[#7cb342]">Date Captured</h3>
                  <p className="text-lg font-semibold text-[#33691e]">{formatDate(activeImage.date)}</p>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-[#7cb342]">Location</h3>
                  <p className="text-lg font-semibold text-[#33691e]">{activeImage.location}</p>
                </div>

                <div className="pt-4 border-t border-[#d1e8cf]">
                  <h3 className="text-sm font-medium text-[#7cb342] mb-2">Actions</h3>
                  <div className="flex space-x-2">
                    <Button className="flex-1 bg-[#8bc34a] hover:bg-[#7cb342] text-white">
                      <Download className="h-4 w-4 mr-1" />
                      Download
                    </Button>
                    <Button
                      variant="outline"
                      className="flex-1 border-[#aed581] text-[#558b2f] hover:bg-[#f1f8e9] hover:text-[#33691e]"
                    >
                      <Tag className="h-4 w-4 mr-1" />
                      Relabel
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
