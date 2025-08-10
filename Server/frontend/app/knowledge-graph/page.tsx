'use client'

import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Slider } from '@/components/ui/slider'

import { 
  Loader2, 
  Search, 
  Network, 
  Database, 
  Filter,
  Zap,
  Eye,
  BarChart3,
  Maximize2,
  Download,
  RefreshCw,
  Info,
  Settings
} from 'lucide-react'
import { knowledgeGraphApi, apiUtils } from '@/lib/api'
import { KnowledgeGraphData, GraphStats as IGraphStats, GraphFilterRequest, GraphNode, GraphEdge } from '@/types'
import KnowledgeGraphVisualizer from '@/components/knowledge-graph/KnowledgeGraphVisualizer'
import GraphStatsComponent from '@/components/knowledge-graph/GraphStats'
import NodeDetails from '@/components/knowledge-graph/NodeDetails'

export default function KnowledgeGraphPage() {
  // State management
  const [graphData, setGraphData] = useState<KnowledgeGraphData | null>(null)
  const [graphStats, setGraphStats] = useState<IGraphStats | null>(null)
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const [searchQuery, setSearchQuery] = useState('')
  const [filters, setFilters] = useState<GraphFilterRequest>({
    limit: 100,
    min_similarity: 0.7
  })
  const [activeView, setActiveView] = useState<'graph' | 'stats' | 'details'>('graph')

  // Fetch initial data
  const fetchGraphData = useCallback(async () => {
    setIsLoading(true)
    setError('')
    
    try {
      const [data, stats] = await Promise.all([
        knowledgeGraphApi.getKnowledgeGraph({
          limit: filters.limit,
          min_similarity: filters.min_similarity,
          search_query: searchQuery || undefined,
          cluster_count: 8
        }),
        knowledgeGraphApi.getGraphStats()
      ])
      
      setGraphData(data)
      setGraphStats(stats)
    } catch (err) {
      setError(apiUtils.formatError(err))
    } finally {
      setIsLoading(false)
    }
  }, [filters, searchQuery])

  // Search with debouncing
  const performSearch = useCallback(async () => {
    if (!searchQuery.trim()) {
      await fetchGraphData()
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const data = await knowledgeGraphApi.searchKnowledgeGraph({
        ...filters,
        search_query: searchQuery
      })
      setGraphData(data)
    } catch (err) {
      setError(apiUtils.formatError(err))
    } finally {
      setIsLoading(false)
    }
  }, [searchQuery, filters, fetchGraphData])

  // Initial load
  useEffect(() => {
    fetchGraphData()
  }, [fetchGraphData])

  // Handle node selection
  const handleNodeClick = useCallback((node: GraphNode) => {
    setSelectedNode(node)
    setActiveView('details')
  }, [])

  // Handle export
  const handleExport = useCallback(() => {
    if (!graphData) return
    
    const dataStr = JSON.stringify(graphData, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `knowledge-graph-${new Date().toISOString().split('T')[0]}.json`
    link.click()
    URL.revokeObjectURL(url)
  }, [graphData])

  // Compute graph metrics
  const graphMetrics = useMemo(() => {
    if (!graphData) return null

    const nodeCount = graphData.nodes.length
    const edgeCount = graphData.edges.length
    const clusterCount = Object.keys(graphData.clusters).length
    const avgConnections = nodeCount > 0 ? (edgeCount * 2) / nodeCount : 0
    
    // Find most connected node
    const nodeDegrees = new Map<string, number>()
    graphData.edges.forEach(edge => {
      nodeDegrees.set(edge.source, (nodeDegrees.get(edge.source) || 0) + 1)
      nodeDegrees.set(edge.target, (nodeDegrees.get(edge.target) || 0) + 1)
    })
    
    const maxDegree = Math.max(...Array.from(nodeDegrees.values()), 0)
    const mostConnectedNode = Array.from(nodeDegrees.entries())
      .find(([_, degree]) => degree === maxDegree)?.[0]

    return {
      nodeCount,
      edgeCount,
      clusterCount,
      avgConnections: avgConnections.toFixed(1),
      maxDegree,
      mostConnectedNode
    }
  }, [graphData])

  if (!graphStats?.collection_exists) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Knowledge Graph</h1>
            <p className="text-gray-600 mt-1">Visualize the live knowledge database</p>
          </div>
        </div>

        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <CardTitle className="text-red-800 flex items-center">
              <Database className="h-5 w-5 mr-2" />
              Collection Not Found
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-red-700 mb-4">
              The collection &ldquo;Opal_db_1000&rdquo; was not found in the Qdrant database.
            </p>
            {graphStats?.available_collections && graphStats.available_collections.length > 0 && (
              <div>
                <p className="text-red-700 mb-2">Available collections:</p>
                <div className="flex flex-wrap gap-2">
                  {graphStats.available_collections.map(collection => (
                    <Badge key={collection} variant="outline" className="text-red-700 border-red-300">
                      {collection}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Knowledge Graph</h1>
          <p className="text-gray-600 mt-1">Visualize and explore the live knowledge database</p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            onClick={fetchGraphData}
            disabled={isLoading}
            variant="outline"
            size="sm"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button
            onClick={handleExport}
            disabled={!graphData}
            variant="outline"
            size="sm"
          >
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      {graphMetrics && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-blue-600">{graphMetrics.nodeCount}</div>
              <div className="text-sm text-gray-600">Nodes</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-green-600">{graphMetrics.edgeCount}</div>
              <div className="text-sm text-gray-600">Connections</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-purple-600">{graphMetrics.clusterCount}</div>
              <div className="text-sm text-gray-600">Clusters</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-orange-600">{graphMetrics.avgConnections}</div>
              <div className="text-sm text-gray-600">Avg Connections</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-red-600">{graphMetrics.maxDegree}</div>
              <div className="text-sm text-gray-600">Max Degree</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Filter className="h-5 w-5 mr-2" />
            Search & Filters
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex space-x-4">
            <div className="flex-1">
              <Input
                placeholder="Search knowledge graph..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && performSearch()}
              />
            </div>
            <Button onClick={performSearch} disabled={isLoading}>
              <Search className="h-4 w-4 mr-2" />
              Search
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Node Limit</label>
              <select 
                value={filters.limit.toString()} 
                onChange={(e) => setFilters(prev => ({ ...prev, limit: parseInt(e.target.value) }))}
                className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <option value="50">50 nodes</option>
                <option value="100">100 nodes</option>
                <option value="200">200 nodes</option>
                <option value="500">500 nodes</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Similarity Threshold: {filters.min_similarity.toFixed(2)}
              </label>
              <Slider
                value={[filters.min_similarity]}
                onValueChange={(value) => setFilters(prev => ({ ...prev, min_similarity: value[0] }))}
                min={0.1}
                max={1.0}
                step={0.05}
                className="w-full"
              />
            </div>

            <div className="flex items-end">
              <Button
                onClick={fetchGraphData}
                disabled={isLoading}
                className="w-full"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Zap className="h-4 w-4 mr-2" />
                )}
                Apply Filters
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4">
            <p className="text-red-700">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Main Content */}
      <Tabs value={activeView} onValueChange={(value) => setActiveView(value as any)}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="graph" className="flex items-center">
            <Network className="h-4 w-4 mr-2" />
            Graph View
          </TabsTrigger>
          <TabsTrigger value="stats" className="flex items-center">
            <BarChart3 className="h-4 w-4 mr-2" />
            Statistics
          </TabsTrigger>
          <TabsTrigger value="details" className="flex items-center">
            <Info className="h-4 w-4 mr-2" />
            Node Details
          </TabsTrigger>
        </TabsList>

        <TabsContent value="graph" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center">
                  <Network className="h-5 w-5 mr-2" />
                  Interactive Knowledge Graph
                </span>
                <Button
                  onClick={() => setActiveView('stats')}
                  variant="outline"
                  size="sm"
                >
                  <Maximize2 className="h-4 w-4 mr-2" />
                  Full Analysis
                </Button>
              </CardTitle>
              <CardDescription>
                Click on nodes to explore connections. Drag to navigate. Scroll to zoom.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex items-center justify-center h-96">
                  <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
                  <span className="ml-2 text-gray-600">Loading knowledge graph...</span>
                </div>
              ) : graphData ? (
                <KnowledgeGraphVisualizer
                  data={graphData}
                  onNodeClick={handleNodeClick}
                  selectedNode={selectedNode}
                />
              ) : (
                <div className="flex items-center justify-center h-96">
                  <div className="text-center">
                    <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">No graph data available</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="stats" className="space-y-4">
          <GraphStatsComponent 
            graphData={graphData} 
            graphStats={graphStats} 
            isLoading={isLoading} 
          />
        </TabsContent>

        <TabsContent value="details" className="space-y-4">
          <NodeDetails 
            node={selectedNode} 
            graphData={graphData}
            onNodeSelect={handleNodeClick}
          />
        </TabsContent>
      </Tabs>
    </div>
  )
}
