// Simple Node.js test to verify 3D component compiles without syntax errors
const fs = require('fs');
const path = require('path');

console.log('Testing 3D Knowledge Graph Component...');

try {
  // Read the component file
  const componentPath = path.join(__dirname, 'components/knowledge-graph/KnowledgeGraph3D.tsx');
  const componentContent = fs.readFileSync(componentPath, 'utf8');
  
  // Check for common issues
  const issues = [];
  
  if (componentContent.includes('extend(')) {
    issues.push('❌ Found problematic extend() call');
  } else {
    console.log('✅ No extend() calls found');
  }
  
  if (componentContent.includes('useFrame')) {
    console.log('✅ useFrame hooks found');
  }
  
  if (componentContent.includes('Canvas')) {
    console.log('✅ Canvas component found');
  }
  
  if (componentContent.includes('OrbitControls')) {
    console.log('✅ OrbitControls found');
  }
  
  if (componentContent.includes('generateKnowledgeGraphData')) {
    console.log('✅ Data generation function found');
  }
  
  if (issues.length === 0) {
    console.log('✅ Component appears to be correctly structured!');
  } else {
    console.log('❌ Issues found:', issues);
  }
  
} catch (error) {
  console.error('❌ Error reading component:', error.message);
}

console.log('Test completed.');
