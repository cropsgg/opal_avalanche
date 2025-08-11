'use client';

import React, { useRef, useMemo, useState, useCallback } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Html } from '@react-three/drei';
import * as THREE from 'three';
import type { KnowledgeGraphData } from '@/types';

interface Node3DProps {
  position: [number, number, number];
  size: number;
  color: string;
  label: string;
  onClick: () => void;
  selected: boolean;
  importance: number;
}

const Node3D: React.FC<Node3DProps> = ({ 
  position, 
  size, 
  color, 
  label, 
  onClick, 
  selected,
  importance 
}) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  useFrame((state) => {
    if (meshRef.current) {
      // Gentle rotation based on importance
      meshRef.current.rotation.y += importance * 0.01;
      
      // Floating animation
      meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 2) * (importance * 5);
      
      // Scale animation on hover/select
      const targetScale = selected ? 1.5 : hovered ? 1.2 : 1.0;
      meshRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.1);
    }
  });

  return (
    <group position={position}>
      <mesh
        ref={meshRef}
        onClick={onClick}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <sphereGeometry args={[size / 20, 32, 32]} />
        <meshStandardMaterial 
          color={color}
          emissive={selected ? color : '#000000'}
          emissiveIntensity={selected ? 0.3 : 0}
          metalness={0.8}
          roughness={0.2}
        />
      </mesh>
      
      {/* Glowing ring for important nodes */}
      {importance > 0.8 && (
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <ringGeometry args={[size / 15, size / 12, 32]} />
          <meshBasicMaterial 
            color={color} 
            transparent 
            opacity={0.3}
            side={THREE.DoubleSide}
          />
        </mesh>
      )}

      {/* Node label */}
      {(hovered || selected) && (
        <Html distanceFactor={10}>
          <div className="bg-black/80 text-white px-2 py-1 rounded text-xs max-w-xs">
            {label}
          </div>
        </Html>
      )}
    </group>
  );
};

interface Edge3DProps {
  start: [number, number, number];
  end: [number, number, number];
  opacity: number;
  color?: string;
}

const Edge3D: React.FC<Edge3DProps> = ({ start, end, opacity, color = '#ffffff' }) => {
  const points = useMemo(() => [
    new THREE.Vector3(...start),
    new THREE.Vector3(...end)
  ], [start, end]);

  const lineGeometry = useMemo(() => {
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    return geometry;
  }, [points]);

  return (
    <line>
      <bufferGeometry attach="geometry" {...lineGeometry} />
      <lineBasicMaterial 
        attach="material" 
        color={color} 
        transparent 
        opacity={opacity * 0.3}
      />
    </line>
  );
};

const ParticleSystem: React.FC = () => {
  const particlesRef = useRef<THREE.Points>(null);
  
  const { positions, colors } = useMemo(() => {
    const count = 200;
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    
    for (let i = 0; i < count; i++) {
      // Random positions in a sphere around the graph
      const radius = 800 + Math.random() * 400;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.random() * Math.PI;
      
      positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = radius * Math.cos(phi);
      
      // Subtle colors
      colors[i * 3] = 0.3 + Math.random() * 0.7;
      colors[i * 3 + 1] = 0.3 + Math.random() * 0.7;
      colors[i * 3 + 2] = 0.8 + Math.random() * 0.2;
    }
    
    return { positions, colors };
  }, []);

  useFrame(() => {
    if (particlesRef.current) {
      particlesRef.current.rotation.y += 0.0005;
      particlesRef.current.rotation.x += 0.0002;
    }
  });

  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
        <bufferAttribute
          attach="attributes-color"
          args={[colors, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        size={2}
        vertexColors
        transparent
        opacity={0.6}
        sizeAttenuation={true}
      />
    </points>
  );
};

const CameraController: React.FC = () => {
  const { camera } = useThree();
  
  useFrame((state) => {
    // Smooth camera movement
    camera.position.x = Math.sin(state.clock.elapsedTime * 0.1) * 100;
    camera.position.z += (600 - camera.position.z) * 0.01;
    camera.lookAt(0, 0, 0);
  });

  return null;
};

interface KnowledgeGraph3DProps {
  selectedNode?: string;
  onNodeSelect?: (nodeId: string) => void;
  showEdges?: boolean;
  clusterFilter?: number[];
  graphData?: KnowledgeGraphData;
}

const KnowledgeGraph3D: React.FC<KnowledgeGraph3DProps> = ({
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

  const handleNodeClick = useCallback((nodeId: string) => {
    onNodeSelect?.(nodeId);
  }, [onNodeSelect]);

  return (
    <div className="w-full h-full">
      <Canvas
        camera={{ position: [500, 300, 800], fov: 75 }}
        className="bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900"
      >
        {/* Lighting */}
        <ambientLight intensity={0.6} />
        <pointLight position={[100, 100, 100]} intensity={1.0} color="#ffffff" />
        <pointLight position={[-100, -100, -100]} intensity={0.5} color="#4f46e5" />
        <spotLight 
          position={[0, 500, 0]} 
          angle={Math.PI / 4} 
          penumbra={0.5} 
          intensity={0.8}
          color="#8b5cf6"
        />

        {/* Background particles */}
        <ParticleSystem />

        {/* Nodes */}
        {filteredNodes.map((node) => (
          <Node3D
            key={node.id}
            position={[
              (node.position.x || 0) / 2, 
              (node.position.y || 0) / 2, 
              ((node.position as any).z || Math.random() * 100 - 50) / 2
            ]}
            size={node.size}
            color={node.color}
            label={node.label}
            onClick={() => handleNodeClick(node.id)}
            selected={selectedNode === node.id}
            importance={node.metadata?.importanceScore || 0.5}
          />
        ))}

        {/* Edges */}
        {showEdges && filteredEdges.map((edge, index) => {
          const sourceNode = filteredNodes.find(n => n.id === edge.source);
          const targetNode = filteredNodes.find(n => n.id === edge.target);
          
          if (!sourceNode || !targetNode) return null;
          
          return (
            <Edge3D
              key={`${edge.source}-${edge.target}-${index}`}
              start={[
                (sourceNode.position.x || 0) / 2, 
                (sourceNode.position.y || 0) / 2, 
                ((sourceNode.position as any).z || Math.random() * 100 - 50) / 2
              ]}
              end={[
                (targetNode.position.x || 0) / 2, 
                (targetNode.position.y || 0) / 2, 
                ((targetNode.position as any).z || Math.random() * 100 - 50) / 2
              ]}
              opacity={edge.weight}
              color={selectedNode === edge.source || selectedNode === edge.target ? '#fbbf24' : '#6b7280'}
            />
          );
        })}

        {/* Central reference point */}
        <mesh position={[0, 0, 0]}>
          <sphereGeometry args={[2, 16, 16]} />
          <meshBasicMaterial color="#fbbf24" transparent opacity={0.5} />
        </mesh>

        {/* Controls */}
        <OrbitControls 
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          minDistance={200}
          maxDistance={1500}
          autoRotate={false}
          autoRotateSpeed={0.5}
        />

        {/* Camera animation */}
        <CameraController />
      </Canvas>

      {/* UI Overlay */}
      <div className="absolute top-4 left-4 bg-black/80 text-white p-4 rounded-lg backdrop-blur-sm">
        <h3 className="font-bold text-lg mb-2">3D Knowledge Graph</h3>
        <div className="text-sm space-y-1">
          <div>📊 {filteredNodes.length} Documents</div>
          <div>🕸️ {filteredEdges.length} Connections</div>
          <div>⚖️ {Object.keys(graphData?.clusters || {}).length} Clusters</div>
          <div>🔗 Vector Database</div>
        </div>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 right-4 bg-black/80 text-white p-4 rounded-lg backdrop-blur-sm max-h-80 overflow-y-auto">
        <h4 className="font-bold mb-2">Legal Domains</h4>
        <div className="space-y-1 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'hsl(0, 70%, 60%)' }}></div>
            <span>Constitutional Interpretation</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'hsl(30, 70%, 60%)' }}></div>
            <span>Criminal Jurisprudence</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'hsl(60, 70%, 60%)' }}></div>
            <span>Corporate Governance</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'hsl(90, 70%, 60%)' }}></div>
            <span>Environmental Protection</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'hsl(120, 70%, 60%)' }}></div>
            <span>Information Technology</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'hsl(150, 70%, 60%)' }}></div>
            <span>Intellectual Property</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'hsl(180, 70%, 60%)' }}></div>
            <span>Administrative Law</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'hsl(210, 70%, 60%)' }}></div>
            <span>International Law</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'hsl(240, 70%, 60%)' }}></div>
            <span>Banking & Finance</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'hsl(270, 70%, 60%)' }}></div>
            <span>Media & Communication</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'hsl(300, 70%, 60%)' }}></div>
            <span>Healthcare Law</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'hsl(330, 70%, 60%)' }}></div>
            <span>Education Rights</span>
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="absolute top-4 right-4 bg-black/80 text-white p-3 rounded-lg backdrop-blur-sm text-xs">
        <div>🖱️ Drag to rotate</div>
        <div>🔍 Scroll to zoom</div>
        <div>👆 Click nodes to select</div>
      </div>
    </div>
  );
};

export default KnowledgeGraph3D;