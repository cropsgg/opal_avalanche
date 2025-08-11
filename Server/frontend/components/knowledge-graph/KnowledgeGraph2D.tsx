'use client';

import React, { useMemo } from 'react';
import type { KnowledgeGraphData } from '@/types';

interface KnowledgeGraph2DProps {
  selectedNode?: string;
  onNodeSelect?: (nodeId: string) => void;
  showEdges?: boolean;
  clusterFilter?: number[];
  graphData?: KnowledgeGraphData;
}

const KnowledgeGraph2D: React.FC<KnowledgeGraph2DProps> = ({
  selectedNode,
  onNodeSelect,
  showEdges = true,
  clusterFilter,
  graphData
}) => {
  const { nodes = [], edges = [] } = graphData || {};
  
  const filteredNodes = useMemo(() => {
    if (!clusterFilter || clusterFilter.length === 0) return nodes;
    return nodes.filter(node => clusterFilter.includes(node.cluster));
  }, [nodes, clusterFilter]);

  const filteredEdges = useMemo(() => {
    if (!showEdges || !clusterFilter || clusterFilter.length === 0) return edges;
    const nodeIds = new Set(filteredNodes.map(n => n.id));
    return edges.filter(edge => nodeIds.has(edge.source) && nodeIds.has(edge.target));
  }, [edges, showEdges, filteredNodes, clusterFilter]);

  // Convert 3D positions to 2D for display
  const viewBox = useMemo(() => {
    if (filteredNodes.length === 0) return "0 0 800 600";
    
    const minX = Math.min(...filteredNodes.map(n => n.position.x));
    const maxX = Math.max(...filteredNodes.map(n => n.position.x));
    const minY = Math.min(...filteredNodes.map(n => n.position.y));
    const maxY = Math.max(...filteredNodes.map(n => n.position.y));
    
    const width = Math.max(maxX - minX, 800);
    const height = Math.max(maxY - minY, 600);
    
    return `${minX - 100} ${minY - 100} ${width + 200} ${height + 200}`;
  }, [filteredNodes]);

  return (
    <div className="w-full h-full bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 rounded-lg overflow-hidden relative">
      <svg 
        className="w-full h-full" 
        viewBox={viewBox}
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Background gradient */}
        <defs>
          <radialGradient id="bgGradient" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="rgba(139, 92, 246, 0.1)" />
            <stop offset="100%" stopColor="rgba(15, 23, 42, 0.3)" />
          </radialGradient>
          
          {/* Node glow effects */}
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge> 
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        
        <rect width="100%" height="100%" fill="url(#bgGradient)" />

        {/* Edges */}
        {showEdges && filteredEdges.map((edge, index) => {
          const sourceNode = filteredNodes.find(n => n.id === edge.source);
          const targetNode = filteredNodes.find(n => n.id === edge.target);
          
          if (!sourceNode || !targetNode) return null;
          
          const isHighlighted = selectedNode === edge.source || selectedNode === edge.target;
          
          return (
            <line
              key={`${edge.source}-${edge.target}-${index}`}
              x1={sourceNode.position.x}
              y1={sourceNode.position.y}
              x2={targetNode.position.x}
              y2={targetNode.position.y}
              stroke={isHighlighted ? '#fbbf24' : '#6b7280'}
              strokeWidth={isHighlighted ? 2 : 1}
              opacity={edge.weight * (isHighlighted ? 0.8 : 0.3)}
              strokeDasharray={isHighlighted ? "none" : "5,5"}
            />
          );
        })}

        {/* Nodes */}
        {filteredNodes.map((node) => {
          const isSelected = selectedNode === node.id;
          const radius = node.size / 4;
          
          return (
            <g 
              key={node.id}
              className="cursor-pointer"
              onClick={() => onNodeSelect?.(node.id)}
            >
              {/* Node glow for important nodes */}
              {(node.metadata?.importanceScore || 0) > 0.8 && (
                <circle
                  cx={node.position.x}
                  cy={node.position.y}
                  r={radius + 5}
                  fill={node.color}
                  opacity={0.3}
                  filter="url(#glow)"
                />
              )}
              
              {/* Main node */}
              <circle
                cx={node.position.x}
                cy={node.position.y}
                r={radius}
                fill={node.color}
                stroke={isSelected ? '#fbbf24' : '#ffffff'}
                strokeWidth={isSelected ? 3 : 1}
                opacity={0.9}
                filter={isSelected ? "url(#glow)" : "none"}
                className="transition-all duration-200 hover:opacity-100"
              />
              
              {/* Blockchain verified indicator */}
              {node.metadata?.blockchainHash && (
                <circle
                  cx={node.position.x + radius * 0.7}
                  cy={node.position.y - radius * 0.7}
                  r={3}
                  fill="#10b981"
                  stroke="#ffffff"
                  strokeWidth={1}
                />
              )}
              
              {/* Label on hover/select */}
              {isSelected && (
                <g>
                  <rect
                    x={node.position.x - 100}
                    y={node.position.y - radius - 25}
                    width={200}
                    height={20}
                    fill="rgba(0, 0, 0, 0.8)"
                    rx={10}
                  />
                  <text
                    x={node.position.x}
                    y={node.position.y - radius - 10}
                    textAnchor="middle"
                    fill="white"
                    fontSize="12"
                    fontWeight="bold"
                  >
                    {node.label.length > 30 ? node.label.substring(0, 30) + "..." : node.label}
                  </text>
                </g>
              )}
            </g>
          );
        })}

        {/* Central reference point */}
        <circle
          cx={0}
          cy={0}
          r={4}
          fill="#fbbf24"
          opacity={0.5}
        />
      </svg>

      {/* UI Overlay */}
      <div className="absolute top-4 left-4 bg-black/80 text-white p-4 rounded-lg backdrop-blur-sm">
        <h3 className="font-bold text-lg mb-2">Knowledge Graph</h3>
        <div className="text-sm space-y-1">
          <div>📊 {filteredNodes.length} Documents</div>
          <div>🕸️ {filteredEdges.length} Connections</div>
          <div>⚖️ {Object.keys(graphData?.clusters || {}).length} Clusters</div>
          <div>🔗 Vector Database</div>
        </div>
      </div>

      {/* Legend */}
      {graphData?.clusters && Object.keys(graphData.clusters).length > 0 && (
        <div className="absolute bottom-4 right-4 bg-black/80 text-white p-4 rounded-lg backdrop-blur-sm">
          <h4 className="font-bold mb-2">Cluster Legend</h4>
          <div className="space-y-1 text-xs">
            {Object.entries(graphData.clusters).slice(0, 8).map(([id, cluster]: [string, any]) => (
              <div key={id} className="flex items-center gap-2">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: cluster.color || `hsl(${parseInt(id) * 45}, 70%, 60%)` }}
                ></div>
                <span>Cluster {id}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="absolute top-4 right-4 bg-black/80 text-white p-3 rounded-lg backdrop-blur-sm text-xs">
        <div>👆 Click nodes to select</div>
        <div>🔍 Use filters to explore</div>
        <div>⚖️ Green dots = Verified</div>
      </div>
    </div>
  );
};

export default KnowledgeGraph2D;
