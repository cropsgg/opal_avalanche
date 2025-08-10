'use client'

import React, { useMemo } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { KnowledgeGraphData, GraphNode } from '@/types'
import { 
  Info, 
  Network, 
  FileText, 
  Tag, 
  Calendar,
  ExternalLink,
  Copy,
  Eye
} from 'lucide-react'

interface NodeDetailsProps {
  node: GraphNode | null
  graphData: KnowledgeGraphData | null
  onNodeSelect?: (node: GraphNode) => void
}

export default function NodeDetails({ node, graphData, onNodeSelect }: NodeDetailsProps) {
  // Find connected nodes
  const connectedNodes = useMemo(() => {
    if (!node || !graphData) return []

    const connections = graphData.edges
      .filter(edge => edge.source === node.id || edge.target === node.id)
      .map(edge => {
        const connectedNodeId = edge.source === node.id ? edge.target : edge.source
        const connectedNode = graphData.nodes.find(n => n.id === connectedNodeId)
        return {
          node: connectedNode,
          edge: edge,
          weight: edge.weight
        }
      })
      .filter(item => item.node)
      .sort((a, b) => b.weight - a.weight)

    return connections
  }, [node, graphData])

  // Get cluster information
  const clusterInfo = useMemo(() => {
    if (!node || !graphData) return null

    const cluster = graphData.clusters[node.cluster.toString()]
    if (!cluster) return null

    const clusterNodes = graphData.nodes.filter(n => n.cluster === node.cluster)
    
    return {
      ...cluster,
      nodes: clusterNodes,
      totalSize: cluster.size
    }
  }, [node, graphData])

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  if (!node) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center">
            <Eye className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Select a node from the graph to view details</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Node Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center">
              <div
                className="w-4 h-4 rounded-full mr-3"
                style={{ backgroundColor: node.color }}
              />
              Node Details
            </span>
            <Badge variant="outline">
              ID: {node.id}
            </Badge>
          </CardTitle>
          <CardDescription>
            Detailed information about the selected knowledge node
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium text-gray-600">Label</label>
            <div className="flex items-center justify-between mt-1">
              <p className="text-lg font-medium">{node.label}</p>
              <Button
                onClick={() => copyToClipboard(node.label)}
                variant="outline"
                size="sm"
              >
                <Copy className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-600">Content</label>
            <div className="mt-1 p-3 bg-gray-50 rounded-lg max-h-48 overflow-y-auto">
              <p className="text-sm whitespace-pre-wrap">{node.content}</p>
            </div>
            <div className="flex justify-end mt-2">
              <Button
                onClick={() => copyToClipboard(node.content)}
                variant="outline"
                size="sm"
              >
                <Copy className="h-4 w-4 mr-2" />
                Copy Content
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-600">Cluster</label>
              <div className="flex items-center mt-1">
                <div
                  className="w-3 h-3 rounded-full mr-2"
                  style={{ backgroundColor: node.color }}
                />
                <span className="text-lg font-medium">{node.cluster}</span>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-600">Node Size</label>
              <p className="text-lg font-medium mt-1">{node.size.toFixed(1)}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-600">Position</label>
              <p className="text-sm text-gray-500 mt-1">
                ({node.position.x.toFixed(0)}, {node.position.y.toFixed(0)})
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-600">Connections</label>
              <p className="text-lg font-medium mt-1">{connectedNodes.length}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Metadata */}
      {node.metadata && Object.keys(node.metadata).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Tag className="h-5 w-5 mr-2" />
              Metadata
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(node.metadata).map(([key, value]) => (
                <div key={key}>
                  <label className="text-sm font-medium text-gray-600 capitalize">
                    {key.replace(/_/g, ' ')}
                  </label>
                  <div className="mt-1">
                    {typeof value === 'string' || typeof value === 'number' ? (
                      <p className="text-sm text-gray-800">{value}</p>
                    ) : Array.isArray(value) ? (
                      <div className="flex flex-wrap gap-1">
                        {value.map((item, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {item}
                          </Badge>
                        ))}
                      </div>
                    ) : (
                      <pre className="text-xs bg-gray-50 p-2 rounded overflow-x-auto">
                        {JSON.stringify(value, null, 2)}
                      </pre>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Cluster Information */}
      {clusterInfo && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Network className="h-5 w-5 mr-2" />
              Cluster {node.cluster}
            </CardTitle>
            <CardDescription>
              Information about the cluster this node belongs to
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-600">Cluster Size</label>
                <p className="text-lg font-medium mt-1">{clusterInfo.totalSize} nodes</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600">Color</label>
                <div className="flex items-center mt-1">
                  <div
                    className="w-6 h-6 rounded-full mr-2 border"
                    style={{ backgroundColor: clusterInfo.color }}
                  />
                  <span className="text-sm text-gray-600">{clusterInfo.color}</span>
                </div>
              </div>
            </div>

            {clusterInfo.nodes && clusterInfo.nodes.length > 1 && (
              <div>
                <label className="text-sm font-medium text-gray-600 mb-2 block">
                  Other nodes in this cluster:
                </label>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {clusterInfo.nodes
                    .filter((n: GraphNode) => n.id !== node.id)
                    .slice(0, 10)
                    .map((clusterNode: GraphNode) => (
                      <div
                        key={clusterNode.id}
                        className="flex items-center justify-between p-2 border rounded-lg hover:bg-gray-50 cursor-pointer"
                        onClick={() => onNodeSelect?.(clusterNode)}
                      >
                        <div className="flex items-center">
                          <div
                            className="w-3 h-3 rounded-full mr-2"
                            style={{ backgroundColor: clusterNode.color }}
                          />
                          <span className="text-sm font-medium">{clusterNode.label}</span>
                        </div>
                        <ExternalLink className="h-4 w-4 text-gray-400" />
                      </div>
                    ))}
                  {clusterInfo.nodes.length > 11 && (
                    <p className="text-sm text-gray-500 text-center">
                      And {clusterInfo.nodes.length - 11} more nodes...
                    </p>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Connected Nodes */}
      {connectedNodes.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Network className="h-5 w-5 mr-2" />
              Connected Nodes ({connectedNodes.length})
            </CardTitle>
            <CardDescription>
              Nodes directly connected to this node, sorted by connection strength
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {connectedNodes.map(({ node: connectedNode, edge, weight }) => (
                <div
                  key={connectedNode!.id}
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
                  onClick={() => onNodeSelect?.(connectedNode!)}
                >
                  <div className="flex items-center space-x-3">
                    <div
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: connectedNode!.color }}
                    />
                    <div>
                      <div className="font-medium">{connectedNode!.label}</div>
                      <div className="text-sm text-gray-600">
                        Cluster {connectedNode!.cluster}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-blue-600">
                      {weight.toFixed(2)}
                    </div>
                    <div className="text-xs text-gray-500">similarity</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <FileText className="h-5 w-5 mr-2" />
            Actions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-2">
            <Button
              onClick={() => copyToClipboard(JSON.stringify(node, null, 2))}
              variant="outline"
            >
              <Copy className="h-4 w-4 mr-2" />
              Copy Node Data
            </Button>
            <Button
              onClick={() => copyToClipboard(node.id)}
              variant="outline"
            >
              <Copy className="h-4 w-4 mr-2" />
              Copy ID
            </Button>
            {node.metadata?.url && (
              <Button
                onClick={() => window.open(node.metadata.url, '_blank')}
                variant="outline"
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                Open Source
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
