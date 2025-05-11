"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import {
  ArrowLeft,
  Bird,
  Calendar,
  Clock,
  Heart,
  ImageIcon,
  Leaf,
  Maximize,
  Star,
  Sun,
  Sunrise,
  Timer,
  X,
} from "lucide-react"
import Image from "next/image"
import BirdGallery from "@/components/bird-gallery"
import { getStats } from "@/lib/api"

interface BirdStatsDashboardProps {
  onBack: () => void
}

export default function BirdStatsDashboard({ onBack }: BirdStatsDashboardProps) {
  const [enterGallery, setEnterGallery] = useState(false)
  const [stats, setStats] = useState<any>({
    total_detections: 0,
    bird_detections: 0,
    species_identified: 0,
    average_confidence: 0,
    top_species: [],
    recent_counts: []
  })
  const [loading, setLoading] = useState(true)

  // Fetch stats from the API
  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true)
        const response = await getStats()
        if (response && response.success && response.stats) {
          setStats(response.stats)
        }
      } catch (error) {
        console.error("Error fetching stats:", error)
        // Keep default stats
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  // Get the most common species
  const mostSeenSpecies = stats.top_species && stats.top_species.length > 0 
    ? stats.top_species[0].species 
    : "Cardinal"

  // Get the rarest visitor (last in top species)
  const rarestVisitor = stats.top_species && stats.top_species.length > 0 
    ? stats.top_species[stats.top_species.length - 1].species 
    : "Warbler"

  if (enterGallery) {
    return <BirdGallery />
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#f0f9ff] to-[#e8f5e9] pb-16">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center">
            <Button variant="ghost" size="sm" onClick={onBack} className="mr-2">
              <ArrowLeft className="h-4 w-4 mr-1" />
              Back
            </Button>
            <h1 className="text-xl font-bold text-[#33691e]">Birdhouse Camera Stats</h1>
          </div>
          <div className="flex items-center space-x-2">
            <div className="bg-[#f1f8e9] px-3 py-1 rounded-full text-sm font-medium text-[#558b2f]">
              Last updated: Today, 8:15 AM
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Welcome Banner */}
        <div className="relative rounded-2xl overflow-hidden mb-8 bg-white shadow-sm border border-[#d1e8cf]">
          <div className="absolute top-0 right-0 w-1/3 h-full hidden md:block">
            <Image
              src="/placeholder.svg?height=300&width=400"
              alt="Birds collage"
              fill
              className="object-cover opacity-20"
            />
          </div>
          <div className="relative z-10 p-6 md:w-2/3">
            <h2 className="text-2xl md:text-3xl font-bold text-[#33691e] mb-2">
              Welcome to Your Bird Stats Dashboard!
            </h2>
            <p className="text-[#558b2f] mb-4 max-w-2xl">
              Here's a snapshot of all the wonderful bird activity at your birdhouse. Explore the stats below to see
              what your feathered friends have been up to!
            </p>
            <Button onClick={() => setEnterGallery(true)} className="bg-[#8bc34a] hover:bg-[#7cb342] text-white">
              View Full Gallery
            </Button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Card 1: Recent Visitors */}
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-[#d1e8cf] transform transition-all hover:shadow-md">
            <div className="flex items-center mb-4">
              <div className="bg-[#8bc34a]/10 p-3 rounded-full mr-4">
                <Bird className="h-6 w-6 text-[#558b2f]" />
              </div>
              <h3 className="text-lg font-semibold text-[#33691e]">Recent Visitors</h3>
            </div>
            <div className="mb-2">
              <span className="text-4xl font-bold text-[#558b2f]">14</span>
              <span className="ml-2 text-[#7cb342]">birds</span>
            </div>
            <p className="text-sm text-[#7cb342]">These feathered friends have stopped by since your last visit!</p>
          </div>

          {/* Card 2: Species Count */}
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-[#d1e8cf] transform transition-all hover:shadow-md">
            <div className="flex items-center mb-4">
              <div className="bg-[#8bc34a]/10 p-3 rounded-full mr-4">
                <Leaf className="h-6 w-6 text-[#558b2f]" />
              </div>
              <h3 className="text-lg font-semibold text-[#33691e]">Species Count</h3>
            </div>
            <div className="mb-2">
              <span className="text-4xl font-bold text-[#558b2f]">23</span>
              <span className="ml-2 text-[#7cb342]">species</span>
            </div>
            <p className="text-sm text-[#7cb342]">
              Your birdhouse has attracted an amazing variety of beautiful birds!
            </p>
          </div>

          {/* Card 3: Total Sightings */}
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-[#d1e8cf] transform transition-all hover:shadow-md">
            <div className="flex items-center mb-4">
              <div className="bg-[#8bc34a]/10 p-3 rounded-full mr-4">
                <ImageIcon className="h-6 w-6 text-[#558b2f]" />
              </div>
              <h3 className="text-lg font-semibold text-[#33691e]">Total Sightings</h3>
            </div>
            <div className="mb-2">
              <span className="text-4xl font-bold text-[#558b2f]">342</span>
              <span className="ml-2 text-[#7cb342]">photos</span>
            </div>
            <p className="text-sm text-[#7cb342]">Your camera has captured hundreds of wonderful bird moments!</p>
          </div>

          {/* Card 4: Most Seen Species */}
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-[#d1e8cf] transform transition-all hover:shadow-md">
            <div className="flex items-center mb-4">
              <div className="bg-[#8bc34a]/10 p-3 rounded-full mr-4">
                <Maximize className="h-6 w-6 text-[#558b2f]" />
              </div>
              <h3 className="text-lg font-semibold text-[#33691e]">Most Seen Species</h3>
            </div>
            <div className="mb-2">
              <span className="text-4xl font-bold text-[#558b2f]">{mostSeenSpecies}</span>
            </div>
            <p className="text-sm text-[#7cb342]">Northern Cardinals love your birdhouse with 47 visits so far!</p>
          </div>

          {/* Card 5: Rarest Visitor */}
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-[#d1e8cf] transform transition-all hover:shadow-md">
            <div className="flex items-center mb-4">
              <div className="bg-[#8bc34a]/10 p-3 rounded-full mr-4">
                <Star className="h-6 w-6 text-[#558b2f]" />
              </div>
              <h3 className="text-lg font-semibold text-[#33691e]">Rarest Visitor</h3>
            </div>
            <div className="mb-2">
              <span className="text-4xl font-bold text-[#558b2f]">{rarestVisitor}</span>
            </div>
            <p className="text-sm text-[#7cb342]">You've had just one special visit from this beautiful songbird!</p>
          </div>

          {/* Card 6: Average Daily Sightings */}
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-[#d1e8cf] transform transition-all hover:shadow-md">
            <div className="flex items-center mb-4">
              <div className="bg-[#8bc34a]/10 p-3 rounded-full mr-4">
                <Calendar className="h-6 w-6 text-[#558b2f]" />
              </div>
              <h3 className="text-lg font-semibold text-[#33691e]">Average Daily Sightings</h3>
            </div>
            <div className="mb-2">
              <span className="text-4xl font-bold text-[#558b2f]">5.3</span>
              <span className="ml-2 text-[#7cb342]">birds/day</span>
            </div>
            <p className="text-sm text-[#7cb342]">Your birdhouse sees consistent activity throughout the week!</p>
          </div>

          {/* Card 7: First Visitor */}
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-[#d1e8cf] transform transition-all hover:shadow-md">
            <div className="flex items-center mb-4">
              <div className="bg-[#8bc34a]/10 p-3 rounded-full mr-4">
                <Clock className="h-6 w-6 text-[#558b2f]" />
              </div>
              <h3 className="text-lg font-semibold text-[#33691e]">First Visitor</h3>
            </div>
            <div className="mb-2">
              <span className="text-4xl font-bold text-[#558b2f]">March 12</span>
            </div>
            <p className="text-sm text-[#7cb342]">A friendly Robin was the first to discover your birdhouse!</p>
          </div>

          {/* Card 8: Latest Visitor */}
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-[#d1e8cf] transform transition-all hover:shadow-md">
            <div className="flex items-center mb-4">
              <div className="bg-[#8bc34a]/10 p-3 rounded-full mr-4">
                <Timer className="h-6 w-6 text-[#558b2f]" />
              </div>
              <h3 className="text-lg font-semibold text-[#33691e]">Latest Visitor</h3>
            </div>
            <div className="mb-2">
              <span className="text-4xl font-bold text-[#558b2f]">Chickadee</span>
            </div>
            <p className="text-sm text-[#7cb342]">Spotted today at 7:42 AM enjoying your birdhouse!</p>
          </div>

          {/* Card 9: Longest Visit Streak */}
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-[#d1e8cf] transform transition-all hover:shadow-md">
            <div className="flex items-center mb-4">
              <div className="bg-[#8bc34a]/10 p-3 rounded-full mr-4">
                <Sunrise className="h-6 w-6 text-[#558b2f]" />
              </div>
              <h3 className="text-lg font-semibold text-[#33691e]">Longest Visit Streak</h3>
            </div>
            <div className="mb-2">
              <span className="text-4xl font-bold text-[#558b2f]">16</span>
              <span className="ml-2 text-[#7cb342]">days</span>
            </div>
            <p className="text-sm text-[#7cb342]">Your birdhouse had visitors every day for over two weeks straight!</p>
          </div>

          {/* Card 10: Empty Days */}
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-[#d1e8cf] transform transition-all hover:shadow-md">
            <div className="flex items-center mb-4">
              <div className="bg-[#8bc34a]/10 p-3 rounded-full mr-4">
                <X className="h-6 w-6 text-[#558b2f]" />
              </div>
              <h3 className="text-lg font-semibold text-[#33691e]">Empty Days</h3>
            </div>
            <div className="mb-2">
              <span className="text-4xl font-bold text-[#558b2f]">7</span>
              <span className="ml-2 text-[#7cb342]">days</span>
            </div>
            <p className="text-sm text-[#7cb342]">Only a few days without any bird visitors - they love your setup!</p>
          </div>

          {/* Card 11: Active Hours */}
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-[#d1e8cf] transform transition-all hover:shadow-md">
            <div className="flex items-center mb-4">
              <div className="bg-[#8bc34a]/10 p-3 rounded-full mr-4">
                <Sun className="h-6 w-6 text-[#558b2f]" />
              </div>
              <h3 className="text-lg font-semibold text-[#33691e]">Active Hours</h3>
            </div>
            <div className="mb-2">
              <span className="text-4xl font-bold text-[#558b2f]">7-9 AM</span>
            </div>
            <p className="text-sm text-[#7cb342]">Early morning is the busiest time for your feathered visitors!</p>
          </div>

          {/* Card 12: Favorites Tagged */}
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-[#d1e8cf] transform transition-all hover:shadow-md">
            <div className="flex items-center mb-4">
              <div className="bg-[#8bc34a]/10 p-3 rounded-full mr-4">
                <Heart className="h-6 w-6 text-[#558b2f]" />
              </div>
              <h3 className="text-lg font-semibold text-[#33691e]">Favorites Tagged</h3>
            </div>
            <div className="mb-2">
              <span className="text-4xl font-bold text-[#558b2f]">18</span>
              <span className="ml-2 text-[#7cb342]">photos</span>
            </div>
            <p className="text-sm text-[#7cb342]">You've marked these special moments as your favorites!</p>
          </div>
        </div>

        {/* View Gallery Button */}
        <div className="text-center mt-12">
          <Button
            onClick={() => setEnterGallery(true)}
            className="bg-[#8bc34a] hover:bg-[#7cb342] text-white px-8 py-6 text-lg rounded-full"
          >
            View Full Gallery
          </Button>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white mt-16 border-t border-[#d1e8cf] py-6">
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm text-[#7cb342]">Birdhouse Camera Platform • Updated May 6, 2025</p>
        </div>
      </footer>
    </div>
  )
}
