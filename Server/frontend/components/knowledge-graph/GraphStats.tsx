'use client'

import React, { useMemo } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { KnowledgeGraphData, GraphStats as IGraphStats } from '@/types'
import { 
  BarChart3, 
  Network, 
  Database, 
  Zap, 
  TrendingUp,
  Users,
  Link as LinkIcon,
  Layers
} from 'lucide-react'

interface GraphStatsProps {
  graphData: KnowledgeGraphData | null
  graphStats: IGraphStats | null
  isLoading: boolean
}

export default function GraphStats({ graphData, graphStats, isLoading }: GraphStatsProps) {
  // Compute detailed statistics
  const detailedStats = useMemo(() => {
    if (!graphData) return null

    const nodes = graphData.nodes
    const edges = graphData.edges
    const clusters = graphData.clusters

    // Node statistics
    const avgNodeSize = nodes.reduce((sum, node) => sum + node.size, 0) / nodes.length
    const nodeSizes = nodes.map(n => n.size).sort((a, b) => b - a)
    const maxNodeSize = nodeSizes[0] || 0
    const minNodeSize = nodeSizes[nodeSizes.length - 1] || 0

    // Edge statistics
    const edgeWeights = edges.map(e => e.weight).sort((a, b) => b - a)
    const avgEdgeWeight = edges.reduce((sum, edge) => sum + edge.weight, 0) / edges.length
    const maxEdgeWeight = edgeWeights[0] || 0
    const minEdgeWeight = edgeWeights[edgeWeights.length - 1] || 0

    // Network density
    const maxPossibleEdges = (nodes.length * (nodes.length - 1)) / 2
    const density = maxPossibleEdges > 0 ? (edges.length / maxPossibleEdges) * 100 : 0

    // Degree distribution
    const nodeDegrees = new Map<string, number>()
    edges.forEach(edge => {
      nodeDegrees.set(edge.source, (nodeDegrees.get(edge.source) || 0) + 1)
      nodeDegrees.set(edge.target, (nodeDegrees.get(edge.target) || 0) + 1)
    })

    const degrees = Array.from(nodeDegrees.values()).sort((a, b) => b - a)
    const avgDegree = degrees.reduce((sum, deg) => sum + deg, 0) / degrees.length
    const maxDegree = degrees[0] || 0

    // Most connected nodes
    const topNodes = Array.from(nodeDegrees.entries())
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5)
      .map(([nodeId, degree]) => {
        const node = nodes.find(n => n.id === nodeId)
        return { node, degree }
      })
      .filter(item => item.node)

    // Cluster statistics
    const clusterSizes = Object.values(clusters).map((cluster: any) => cluster.size)
    const avgClusterSize = clusterSizes.reduce((sum, size) => sum + size, 0) / clusterSizes.length
    const largestCluster = Math.max(...clusterSizes)
    const smallestCluster = Math.min(...clusterSizes)

    return {
      nodeStats: {
        total: nodes.length,
        avgSize: avgNodeSize,
        maxSize: maxNodeSize,
        minSize: minNodeSize
      },
      edgeStats: {
        total: edges.length,
        avgWeight: avgEdgeWeight,
        maxWeight: maxEdgeWeight,
        minWeight: minEdgeWeight
      },
      networkStats: {
        density,
        avgDegree,
        maxDegree,
        components: Object.keys(clusters).length
      },
      topNodes,
      clusterStats: {
        total: Object.keys(clusters).length,
        avgSize: avgClusterSize,
        largestSize: largestCluster,
        smallestSize: smallestCluster
      }
    }
  }, [graphData])

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardContent className="p-6">
              <div className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2 mb-4"></div>
                <div className="space-y-2">
                  <div className="h-3 bg-gray-200 rounded"></div>
                  <div className="h-3 bg-gray-200 rounded w-5/6"></div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (!graphData || !detailedStats) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center">
            <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No graph data available for analysis</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Collection Info */}
      {graphStats && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Database className="h-5 w-5 mr-2" />
              Collection Information
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="text-sm text-gray-600">Total Points</div>
                <div className="text-2xl font-bold text-blue-600">
                  {graphStats.total_points?.toLocaleString() || 'Unknown'}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Vector Size</div>
                <div className="text-2xl font-bold text-green-600">
                  {graphStats.vector_size || 'Unknown'}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Status</div>
                <Badge variant="outline" className="text-green-700 border-green-300">
                  {graphStats.collection_status || 'Active'}
                </Badge>
              </div>
              <div>
                <div className="text-sm text-gray-600">Payload Fields</div>
                <div className="text-2xl font-bold text-purple-600">
                  {graphStats.payload_keys?.length || 0}
                </div>
              </div>
            </div>
            
            {graphStats.payload_keys && graphStats.payload_keys.length > 0 && (
              <div className="mt-4">
                <div className="text-sm text-gray-600 mb-2">Available Fields:</div>
                <div className="flex flex-wrap gap-2">
                  {graphStats.payload_keys.map(key => (
                    <Badge key={key} variant="secondary">
                      {key}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Network Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center text-lg">
              <Users className="h-5 w-5 mr-2 text-blue-600" />
              Nodes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600 mb-2">
              {detailedStats.nodeStats.total}
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Avg Size:</span>
                <span>{detailedStats.nodeStats.avgSize.toFixed(1)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Range:</span>
                <span>{detailedStats.nodeStats.minSize.toFixed(0)} - {detailedStats.nodeStats.maxSize.toFixed(0)}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center text-lg">
              <LinkIcon className="h-5 w-5 mr-2 text-green-600" />
              Connections
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600 mb-2">
              {detailedStats.edgeStats.total}
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Avg Weight:</span>
                <span>{detailedStats.edgeStats.avgWeight.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Range:</span>
                <span>{detailedStats.edgeStats.minWeight.toFixed(2)} - {detailedStats.edgeStats.maxWeight.toFixed(2)}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center text-lg">
              <Layers className="h-5 w-5 mr-2 text-purple-600" />
              Clusters
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600 mb-2">
              {detailedStats.clusterStats.total}
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Avg Size:</span>
                <span>{detailedStats.clusterStats.avgSize.toFixed(1)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Range:</span>
                <span>{detailedStats.clusterStats.smallestSize} - {detailedStats.clusterStats.largestSize}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center text-lg">
              <Network className="h-5 w-5 mr-2 text-orange-600" />
              Density
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600 mb-2">
              {detailedStats.networkStats.density.toFixed(1)}%
            </div>
            <div className="space-y-2">
              <Progress value={detailedStats.networkStats.density} className="h-2" />
              <div className="text-sm text-gray-600">
                Network connectivity level
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Connected Nodes */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <TrendingUp className="h-5 w-5 mr-2" />
            Most Connected Nodes
          </CardTitle>
          <CardDescription>
            Nodes with the highest number of connections
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {detailedStats.topNodes.map((item, index) => (
              <div key={item.node!.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gray-100 text-sm font-medium">
                    {index + 1}
                  </div>
                  <div
                    className="w-4 h-4 rounded-full"
                    style={{ backgroundColor: item.node!.color }}
                  />
                  <div>
                    <div className="font-medium">{item.node!.label}</div>
                    <div className="text-sm text-gray-600">
                      Cluster {item.node!.cluster}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-blue-600">{item.degree}</div>
                  <div className="text-sm text-gray-600">connections</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Cluster Distribution */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <BarChart3 className="h-5 w-5 mr-2" />
            Cluster Distribution
          </CardTitle>
          <CardDescription>
            Size and composition of knowledge clusters
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(graphData.clusters).map(([clusterId, cluster]: [string, any]) => (
              <div key={clusterId} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center space-x-3">
                  <div
                    className="w-4 h-4 rounded-full"
                    style={{ backgroundColor: cluster.color }}
                  />
                  <div>
                    <div className="font-medium">Cluster {clusterId}</div>
                    <div className="text-sm text-gray-600">
                      {((cluster.size / detailedStats.nodeStats.total) * 100).toFixed(1)}% of nodes
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold">{cluster.size}</div>
                  <div className="text-sm text-gray-600">nodes</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Network Metrics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Zap className="h-5 w-5 mr-2" />
            Network Metrics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{detailedStats.networkStats.avgDegree.toFixed(1)}</div>
              <div className="text-sm text-gray-600">Average Degree</div>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold text-green-600">{detailedStats.networkStats.maxDegree}</div>
              <div className="text-sm text-gray-600">Max Degree</div>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{detailedStats.networkStats.components}</div>
              <div className="text-sm text-gray-600">Components</div>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold text-orange-600">{detailedStats.networkStats.density.toFixed(2)}%</div>
              <div className="text-sm text-gray-600">Density</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
