'use client'

import React, { useRef, useEffect, useState, useCallback } from 'react'
import dynamic from 'next/dynamic'
import { KnowledgeGraphData, GraphNode, GraphEdge } from '@/types'
import { Button } from '@/components/ui/button'
import { ZoomIn, ZoomOut, Maximize2, RotateCcw } from 'lucide-react'

// Dynamically import ForceGraph2D to avoid SSR issues
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-96">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>
  )
})

interface KnowledgeGraphVisualizerProps {
  data: KnowledgeGraphData
  onNodeClick?: (node: GraphNode) => void
  selectedNode?: GraphNode | null
  height?: number
}

export default function KnowledgeGraphVisualizer({
  data,
  onNodeClick,
  selectedNode,
  height = 600
}: KnowledgeGraphVisualizerProps) {
  const graphRef = useRef<any>()
  const [graphData, setGraphData] = useState<any>(null)
  const [engineRunning, setEngineRunning] = useState(true)

  // Convert our data format to force-graph format
  useEffect(() => {
    if (!data) return

    const convertedData = {
      nodes: data.nodes.map(node => ({
        id: node.id,
        name: node.label,
        val: node.size / 10, // Scale down for visualization
        color: node.color,
        cluster: node.cluster,
        content: node.content,
        metadata: node.metadata,
        x: node.position.x / 100, // Scale down positions
        y: node.position.y / 100,
        fx: undefined, // Remove fixed positioning
        fy: undefined
      })),
      links: data.edges.map(edge => ({
        source: edge.source,
        target: edge.target,
        value: edge.weight,
        label: edge.label
      }))
    }

    setGraphData(convertedData)
  }, [data])

  // Handle node click
  const handleNodeClick = useCallback((node: any) => {
    if (onNodeClick) {
      const originalNode = data.nodes.find(n => n.id === node.id)
      if (originalNode) {
        onNodeClick(originalNode)
      }
    }
  }, [data.nodes, onNodeClick])

  // Handle node hover
  const handleNodeHover = useCallback((node: any) => {
    if (graphRef.current) {
      graphRef.current.d3Force('charge').strength(node ? -300 : -100)
      graphRef.current.d3Force('charge').distanceMax(node ? 200 : 100)
    }
  }, [])

  // Custom node rendering
  const nodeCanvasObject = useCallback((node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
    const label = node.name || ''
    const fontSize = Math.max(12 / globalScale, 3)
    const nodeRadius = Math.sqrt(node.val || 1) * 4
    const x = node.x || 0
    const y = node.y || 0

    // Draw node circle
    ctx.beginPath()
    ctx.arc(x, y, nodeRadius, 0, 2 * Math.PI, false)
    ctx.fillStyle = node.color || '#000'
    ctx.fill()

    // Add border if selected
    if (selectedNode && selectedNode.id === node.id) {
      ctx.strokeStyle = '#fff'
      ctx.lineWidth = 3 / globalScale
      ctx.stroke()
    }

    // Draw label
    if (globalScale > 1) {
      ctx.font = `${fontSize}px Sans-Serif`
      ctx.fillStyle = '#333'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      
      const maxWidth = nodeRadius * 2
      let displayText = label
      
      // Truncate text if too long
      const textWidth = ctx.measureText(displayText).width
      if (textWidth > maxWidth) {
        while (ctx.measureText(displayText + '...').width > maxWidth && displayText.length > 0) {
          displayText = displayText.slice(0, -1)
        }
        displayText += '...'
      }
      
      ctx.fillText(displayText, x, y + nodeRadius + fontSize + 2)
    }
  }, [selectedNode])

  // Custom link rendering
  const linkCanvasObject = useCallback((link: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
    const { source, target, value } = link
    
    // Calculate link width based on weight
    const linkWidth = Math.max(1, (value || 0) * 2) / globalScale
    
    const sourceX = source.x || 0
    const sourceY = source.y || 0
    const targetX = target.x || 0
    const targetY = target.y || 0
    
    // Draw link
    ctx.beginPath()
    ctx.moveTo(sourceX, sourceY)
    ctx.lineTo(targetX, targetY)
    ctx.strokeStyle = `rgba(100, 100, 100, ${Math.min(value || 0, 0.8)})`
    ctx.lineWidth = linkWidth
    ctx.stroke()

    // Draw label if zoom is high enough
    if (globalScale > 2 && link.label) {
      const midX = (sourceX + targetX) / 2
      const midY = (sourceY + targetY) / 2
      
      ctx.font = `${10 / globalScale}px Sans-Serif`
      ctx.fillStyle = '#666'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(link.label, midX, midY)
    }
  }, [])

  // Control functions
  const handleZoomIn = useCallback(() => {
    if (graphRef.current) {
      graphRef.current.zoom(graphRef.current.zoom() * 1.2)
    }
  }, [])

  const handleZoomOut = useCallback(() => {
    if (graphRef.current) {
      graphRef.current.zoom(graphRef.current.zoom() / 1.2)
    }
  }, [])

  const handleResetView = useCallback(() => {
    if (graphRef.current) {
      graphRef.current.zoomToFit(400)
    }
  }, [])

  const handleCenterView = useCallback(() => {
    if (graphRef.current) {
      graphRef.current.centerAt(0, 0, 1000)
    }
  }, [])

  if (!graphData) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="relative">
      {/* Control Panel */}
      <div className="absolute top-4 right-4 z-10 flex flex-col space-y-2">
        <Button
          onClick={handleZoomIn}
          variant="outline"
          size="sm"
          className="bg-white/90 backdrop-blur-sm"
        >
          <ZoomIn className="h-4 w-4" />
        </Button>
        <Button
          onClick={handleZoomOut}
          variant="outline"
          size="sm"
          className="bg-white/90 backdrop-blur-sm"
        >
          <ZoomOut className="h-4 w-4" />
        </Button>
        <Button
          onClick={handleResetView}
          variant="outline"
          size="sm"
          className="bg-white/90 backdrop-blur-sm"
        >
          <Maximize2 className="h-4 w-4" />
        </Button>
        <Button
          onClick={handleCenterView}
          variant="outline"
          size="sm"
          className="bg-white/90 backdrop-blur-sm"
        >
          <RotateCcw className="h-4 w-4" />
        </Button>
      </div>

      {/* Engine Control */}
      <div className="absolute top-4 left-4 z-10">
        <Button
          onClick={() => setEngineRunning(!engineRunning)}
          variant={engineRunning ? "default" : "outline"}
          size="sm"
          className="bg-white/90 backdrop-blur-sm"
        >
          {engineRunning ? 'Pause Physics' : 'Resume Physics'}
        </Button>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-10 bg-white/90 backdrop-blur-sm rounded-lg p-3 text-sm">
        <div className="font-medium mb-2">Legend</div>
        <div className="space-y-1 text-xs">
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
            <span>Node size = Connections</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-1 bg-gray-400 mr-2"></div>
            <span>Edge width = Similarity</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full border-2 border-white mr-2 bg-purple-500"></div>
            <span>Colors = Clusters</span>
          </div>
        </div>
      </div>

      {/* Graph */}
      <div className="border rounded-lg overflow-hidden bg-white">
        <ForceGraph2D
          ref={graphRef}
          graphData={graphData}
          width={undefined} // Auto-size
          height={height}
          backgroundColor="#fafafa"
          onNodeClick={handleNodeClick}
          onNodeHover={handleNodeHover}
          nodeCanvasObject={nodeCanvasObject}
          linkCanvasObject={linkCanvasObject}
          linkDirectionalParticles={2}
          linkDirectionalParticleSpeed={0.01}
          linkDirectionalParticleWidth={2}
          d3AlphaDecay={0.02}
          d3VelocityDecay={0.3}
          cooldownTicks={100}
          warmupTicks={20}
          enableZoomInteraction={true}
          enablePanInteraction={true}
          enableNodeDrag={true}
          nodePointerAreaPaint={(node, color, ctx) => {
            // Increase click area
            ctx.fillStyle = color
            ctx.beginPath()
            const x = node.x || 0
            const y = node.y || 0
            const radius = Math.sqrt(node.val || 1) * 6
            ctx.arc(x, y, radius, 0, 2 * Math.PI, false)
            ctx.fill()
          }}
          onEngineStop={() => setEngineRunning(false)}
        />
      </div>

      {/* Stats Bar */}
      <div className="mt-4 flex justify-between text-sm text-gray-600">
        <div>
          Nodes: {graphData.nodes.length} | Links: {graphData.links.length}
        </div>
        <div>
          Click nodes to explore • Drag to navigate • Scroll to zoom
        </div>
      </div>
    </div>
  )
}
