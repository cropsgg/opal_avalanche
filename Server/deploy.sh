#!/bin/bash

# OPAL Server Deployment Script
set -e

echo "🚀 OPAL Server Deployment"
echo "========================="

# Parse command line arguments
ENVIRONMENT=${1:-development}
PROFILE=${2:-""}

case $ENVIRONMENT in
    "development"|"dev")
        echo "📦 Deploying in DEVELOPMENT mode..."
        COMPOSE_PROFILES=""
        ;;
    "production"|"prod")
        echo "🏭 Deploying in PRODUCTION mode..."
        COMPOSE_PROFILES="--profile production"
        ;;
    *)
        echo "❌ Invalid environment: $ENVIRONMENT"
        echo "Usage: $0 [development|production] [profile]"
        exit 1
        ;;
esac

# Check if required files exist
echo "🔍 Checking required files..."
required_files=("docker-compose.yml" "backend/Dockerfile" "frontend/Dockerfile")
for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "❌ Required file missing: $file"
        exit 1
    fi
done

# Check if environment files exist
if [[ ! -f "backend/.env" ]]; then
    if [[ -f "backend/.env.example" ]]; then
        echo "📝 Creating backend/.env from example..."
        cp backend/.env.example backend/.env
        echo "⚠️  Please update backend/.env with your configuration"
    else
        echo "❌ backend/.env file is required"
        exit 1
    fi
fi

if [[ ! -f "frontend/.env.local" && "$ENVIRONMENT" == "development" ]]; then
    echo "📝 Creating frontend/.env.local for development..."
    echo "SERVER_API_URL=http://localhost:8001" > frontend/.env.local
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down --remove-orphans

# Build and start services
echo "🔨 Building and starting services..."
if [[ "$ENVIRONMENT" == "production" ]]; then
    docker-compose $COMPOSE_PROFILES up --build -d
else
    docker-compose up --build -d backend frontend qdrant
fi

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
services=("backend" "frontend" "qdrant")
if [[ "$ENVIRONMENT" == "production" ]]; then
    services+=("nginx")
fi

for service in "${services[@]}"; do
    echo "🔍 Checking $service health..."
    if docker-compose ps $service | grep -q "healthy\|Up"; then
        echo "✅ $service is running"
    else
        echo "❌ $service is not healthy"
        docker-compose logs $service
        exit 1
    fi
done

# Display service URLs
echo ""
echo "🎉 Deployment completed successfully!"
echo "=================================="

if [[ "$ENVIRONMENT" == "production" ]]; then
    echo "🌐 Application: http://localhost"
    echo "📊 Backend API: http://localhost/api"
    echo "📚 API Docs: http://localhost/docs"
    echo "💾 Qdrant: http://localhost:6333"
else
    echo "🌐 Frontend: http://localhost:3001"
    echo "📊 Backend API: http://localhost:8001"
    echo "📚 API Docs: http://localhost:8001/docs"
    echo "💾 Qdrant: http://localhost:6333"
fi

echo ""
echo "📋 Useful commands:"
echo "  docker-compose logs -f [service]  # View logs"
echo "  docker-compose ps                 # View status"
echo "  docker-compose down               # Stop services"
echo "  docker-compose exec backend bash # Access backend shell"

echo ""
echo "🔧 Next steps:"
echo "1. Configure backend/.env with your settings"
echo "2. Set up Qdrant collection and data"
echo "3. Configure subnet contracts and keys"
echo "4. Test the application functionality"
