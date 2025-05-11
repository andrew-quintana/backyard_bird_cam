"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { ArrowRight, Bird } from "lucide-react"
import Image from "next/image"
import BirdGallery from "@/components/bird-gallery"
import BirdStatsDashboard from "@/components/bird-stats-dashboard"
import { getStats, getResults } from "@/lib/api"

export default function LandingPage() {
  const [enterGallery, setEnterGallery] = useState(false)
  const [showStats, setShowStats] = useState(false)
  const [birdStats, setBirdStats] = useState({
    birdsSinceLastVisit: 0,
    totalSpecies: 0
  })
  const [loading, setLoading] = useState(true)
  
  // Fetch stats from the API
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        
        // Get stats first
        const statsResponse = await getStats()
        if (statsResponse && statsResponse.success && statsResponse.stats) {
          setBirdStats({
            birdsSinceLastVisit: statsResponse.stats.bird_detections || 0,
            totalSpecies: statsResponse.stats.species_identified || 0
          })
        }
      } catch (error) {
        console.error("Error fetching landing page data:", error)
        // Keep default stats
      } finally {
        setLoading(false)
      }
    }
    
    fetchData()
  }, [])

  if (enterGallery) {
    return <BirdGallery />
  }

  if (showStats) {
    return <BirdStatsDashboard onBack={() => setShowStats(false)} />
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Welcome Section */}
      <section className="relative h-[70vh] flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 z-0">
          <Image
            src="/placeholder.svg?height=1080&width=1920"
            alt="Spring background with birds"
            fill
            className="object-cover opacity-30"
            priority
          />
          <div className="absolute inset-0 bg-gradient-to-b from-[#f0f9ff]/70 to-[#e8f5e9]/70" />
        </div>

        <div className="relative z-10 text-center px-4 max-w-3xl mx-auto">
          <div className="inline-block mb-4 bg-white/80 px-4 py-1 rounded-full">
            <span className="text-sm font-medium text-[#558b2f]">Birdhouse Camera Platform</span>
          </div>
          <h1 className="text-4xl md:text-6xl font-bold text-[#33691e] mb-6 leading-tight">
            Welcome Momma, hope you're having a great day!
          </h1>
          <p className="text-xl text-[#558b2f] mb-8 max-w-2xl mx-auto">
            Check out all the beautiful birds that have visited while you were away.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Button
              onClick={() => setEnterGallery(true)}
              className="bg-[#8bc34a] hover:bg-[#7cb342] text-white px-8 py-6 text-lg rounded-full"
            >
              Enter Gallery
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button
              onClick={() => setShowStats(true)}
              variant="outline"
              className="border-[#8bc34a] text-[#558b2f] hover:bg-[#f1f8e9] px-8 py-6 text-lg rounded-full"
            >
              View Stats Dashboard
            </Button>
          </div>
        </div>
      </section>

      {/* Bird Statistics Section */}
      <section className="bg-white py-16">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* Birds Since Last Visit */}
            <div className="bg-[#f1f8e9] rounded-2xl p-8 shadow-sm border border-[#d1e8cf] transform transition-transform hover:scale-105">
              <div className="flex items-center mb-4">
                <div className="bg-[#8bc34a] p-3 rounded-full mr-4">
                  <Bird className="h-8 w-8 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-[#33691e]">Recent Visitors</h2>
              </div>
              <div className="flex items-baseline">
                <span className="text-5xl font-bold text-[#558b2f]">{birdStats.birdsSinceLastVisit}</span>
                <span className="ml-2 text-xl text-[#7cb342]">birds</span>
              </div>
              <p className="mt-4 text-[#7cb342]">These feathered friends have stopped by since your last visit!</p>
            </div>

            {/* Total Species */}
            <div className="bg-[#f1f8e9] rounded-2xl p-8 shadow-sm border border-[#d1e8cf] transform transition-transform hover:scale-105">
              <div className="flex items-center mb-4">
                <div className="bg-[#8bc34a] p-3 rounded-full mr-4">
                  <Bird className="h-8 w-8 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-[#33691e]">Species Count</h2>
              </div>
              <div className="flex items-baseline">
                <span className="text-5xl font-bold text-[#558b2f]">{birdStats.totalSpecies}</span>
                <span className="ml-2 text-xl text-[#7cb342]">species</span>
              </div>
              <p className="mt-4 text-[#7cb342]">
                You're now up to {birdStats.totalSpecies} different bird species that have visited your birdhouse!
              </p>
            </div>
          </div>

          {/* Featured Bird of the Day */}
          <div className="max-w-4xl mx-auto mt-8">
            <div className="bg-[#f1f8e9] rounded-2xl overflow-hidden shadow-sm border border-[#d1e8cf]">
              <div className="p-6">
                <h2 className="text-2xl font-bold text-[#33691e] mb-2">Featured Bird of the Day</h2>
                <p className="text-[#7cb342] mb-4">
                  This beautiful Northern Cardinal has been visiting your birdhouse frequently!
                </p>
              </div>
              <div className="flex flex-col md:flex-row">
                <div className="md:w-1/2 relative">
                  <Image
                    src="/placeholder.svg?height=600&width=800"
                    alt="Featured bird"
                    width={800}
                    height={600}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="md:w-1/2 p-6 bg-white">
                  <h3 className="text-xl font-bold text-[#33691e] mb-2">Northern Cardinal</h3>
                  <p className="text-[#558b2f] mb-4">
                    Cardinals are known for their bright red color and beautiful songs. They mate for life and stay with
                    their partners year-round.
                  </p>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-[#7cb342]">Visits this week:</span>
                      <span className="text-sm font-medium text-[#33691e]">7</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-[#7cb342]">Favorite time:</span>
                      <span className="text-sm font-medium text-[#33691e]">Early morning</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-[#7cb342]">Last seen:</span>
                      <span className="text-sm font-medium text-[#33691e]">Today, 7:42 AM</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="text-center mt-12">
            <Button
              onClick={() => setEnterGallery(true)}
              className="bg-[#8bc34a] hover:bg-[#7cb342] text-white px-6 py-2"
            >
              View All Birds
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      </section>
    </div>
  )
}
