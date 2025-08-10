#!/bin/bash

# OPAL Server Frontend Startup Script

echo "🚀 Starting OPAL Server Frontend..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Copy environment file if it doesn't exist
if [ ! -f ".env.local" ]; then
    if [ -f "env.example" ]; then
        echo "📋 Creating .env.local from example..."
        cp env.example .env.local
        echo "⚠️  Please update .env.local with your configuration"
    fi
fi

# Start the development server
echo "🌐 Starting frontend on http://localhost:3001..."
npm run dev
