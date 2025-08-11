'use client'

import React, { useState, useEffect } from 'react'
import dynamic from 'next/dynamic'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Search, Filter, Eye, EyeOff, BarChart3, Network, Sparkles, Gavel, Scale, Shield, AlertCircle } from 'lucide-react'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { knowledgeGraphApi } from '@/lib/api'
import type { KnowledgeGraphData, GraphStats } from '@/types'

// Dynamically import the 3D component to avoid SSR issues
const KnowledgeGraph3D = dynamic(
  () => import('@/components/knowledge-graph/KnowledgeGraph3D').catch(() => 
    import('@/components/knowledge-graph/KnowledgeGraph2D')
  ), 
  {
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading 3D Knowledge Graph...</p>
        </div>
      </div>
    )
  }
)

export default function KnowledgeGraphPage() {
  const [selectedNode, setSelectedNode] = useState<string>()
  const [showEdges, setShowEdges] = useState(true)
  const [clusterFilter, setClusterFilter] = useState<number[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [graphData, setGraphData] = useState<KnowledgeGraphData | null>(null)
  const [graphStats, setGraphStats] = useState<GraphStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadGraphData()
    loadGraphStats()
  }, [])

  const loadGraphData = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const data = await knowledgeGraphApi.getKnowledgeGraph({
        limit: 100,
        min_similarity: 0.7
      })
      setGraphData(data)
    } catch (error) {
      console.error('Failed to load knowledge graph:', error)
      setError('Failed to load knowledge graph data. Please check if the backend is running and accessible.')
    } finally {
      setIsLoading(false)
    }
  }

  const loadGraphStats = async () => {
    try {
      const stats = await knowledgeGraphApi.getGraphStats()
      setGraphStats(stats)
    } catch (error) {
      console.error('Failed to load graph stats:', error)
    }
  }

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      await loadGraphData()
      return
    }

    try {
      setIsLoading(true)
      const data = await knowledgeGraphApi.searchKnowledgeGraph({
        search_query: searchTerm,
        limit: 100,
        min_similarity: 0.7
      })
      setGraphData(data)
    } catch (error) {
      console.error('Search failed:', error)
      setError('Search failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const selectedNode_data = graphData?.nodes.find(n => n.id === selectedNode)

  const clusterStats = graphData ? Object.entries(graphData.clusters).map(([id, cluster]) => ({
    cluster: parseInt(id),
    topic: `Cluster ${id}`,
    count: cluster.size,
    color: cluster.color
  })) : []

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 flex items-center justify-center">
        <div className="text-center space-y-4">
          <LoadingSpinner size="lg" />
          <p className="text-gray-600 font-medium">Loading knowledge graph...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 flex items-center justify-center">
        <Card className="max-w-md bg-white/80 backdrop-blur-sm">
          <CardContent className="p-6 text-center space-y-4">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto" />
            <h3 className="text-lg font-semibold text-gray-900">Connection Error</h3>
            <p className="text-gray-600">{error}</p>
            <Button onClick={loadGraphData} className="w-full">
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      {/* Hero Header */}
      <section className="relative py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex items-center justify-center mb-6">
            <div className="relative">
              <div className="flex items-center justify-center w-20 h-20 bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl shadow-lg">
                <Network className="h-10 w-10 text-white" />
              </div>
              <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
            </div>
          </div>
          
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 tracking-tight mb-6">
            Knowledge Graph
            <span className="block text-2xl md:text-3xl text-purple-600 font-normal mt-2">
              Interactive Document Network Visualization
            </span>
          </h1>

          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
            Explore document relationships and patterns through an interactive network visualization.
          </p>

          {graphStats && (
            <div className="flex flex-wrap justify-center gap-4 mb-8">
              <Badge variant="secondary" className="bg-purple-100 text-purple-700 px-4 py-2">
                <Gavel className="h-4 w-4 mr-2" />
                {graphStats.total_points || 0} Documents
              </Badge>
              <Badge variant="secondary" className="bg-blue-100 text-blue-700 px-4 py-2">
                <Network className="h-4 w-4 mr-2" />
                {graphData?.edges.length || 0} Connections
              </Badge>
              <Badge variant="secondary" className="bg-green-100 text-green-700 px-4 py-2">
                <Shield className="h-4 w-4 mr-2" />
                Vector Database
              </Badge>
            </div>
          )}
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
        <Card className="bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Network className="h-5 w-5" />
              <span>Knowledge Graph Visualization</span>
            </CardTitle>
            <CardDescription>
              Interactive visualization of document relationships and clusters
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Search Controls */}
            <div className="flex gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search documents..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                    className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
              </div>
              <Button onClick={handleSearch} disabled={isLoading}>
                Search
              </Button>
              <Button onClick={loadGraphData} variant="outline" disabled={isLoading}>
                Reset
              </Button>
            </div>

            {/* Graph Visualization */}
            {graphData && (
              <div className="border-2 border-gray-200 rounded-lg">
                <div className="h-[600px] relative bg-black/5">
                  <KnowledgeGraph3D
                    selectedNode={selectedNode}
                    onNodeSelect={setSelectedNode}
                    showEdges={showEdges}
                    graphData={graphData}
                  />
                </div>
              </div>
            )}

            {/* Selected Node Details */}
            {selectedNode_data && (
              <Card>
                <CardHeader>
                  <CardTitle>Document Details</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-semibold">Label:</h4>
                      <p>{selectedNode_data.label}</p>
                    </div>
                    <div>
                      <h4 className="font-semibold">Content Preview:</h4>
                      <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                        {selectedNode_data.content.slice(0, 300)}...
                      </p>
                    </div>
                    <div>
                      <h4 className="font-semibold">Metadata:</h4>
                      <pre className="text-sm bg-gray-50 p-3 rounded overflow-auto">
                        {JSON.stringify(selectedNode_data.metadata, null, 2)}
                      </pre>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Statistics */}
            {graphStats && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold text-purple-600">
                      {graphStats.total_points || 0}
                    </div>
                    <p className="text-sm text-gray-600">Total Documents</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold text-blue-600">
                      {graphData?.edges.length || 0}
                    </div>
                    <p className="text-sm text-gray-600">Connections</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold text-green-600">
                      {Object.keys(graphData?.clusters || {}).length}
                    </div>
                    <p className="text-sm text-gray-600">Clusters</p>
                  </CardContent>
                </Card>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}