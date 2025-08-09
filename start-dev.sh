#!/bin/bash

# OPAL Development Startup Script
# This script helps you start all services needed for OPAL development

set -e

echo "🏛️  Starting OPAL - GenAI Co-Counsel for Indian Lawyers"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i:$1 >/dev/null 2>&1
}

echo -e "${BLUE}Checking prerequisites...${NC}"

# Check required commands
MISSING_DEPS=()

if ! command_exists node; then
    MISSING_DEPS+=("node")
fi

if ! command_exists python3; then
    MISSING_DEPS+=("python3")
fi

if ! command_exists docker; then
    MISSING_DEPS+=("docker")
fi

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo -e "${RED}❌ Missing dependencies: ${MISSING_DEPS[*]}${NC}"
    echo "Please install the missing dependencies and run this script again."
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites found${NC}"

# Start Docker services (Qdrant, PostgreSQL, Redis)
echo -e "${BLUE}Starting Docker services...${NC}"
if [ -f "infra/docker-compose.yml" ]; then
    cd infra
    docker-compose up -d
    cd ..
    echo -e "${GREEN}✅ Docker services started${NC}"
else
    echo -e "${YELLOW}⚠️  Docker compose file not found. You may need to start services manually.${NC}"
fi

# Wait a bit for services to start
sleep 3

# Check if backend virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo -e "${BLUE}Creating Python virtual environment...${NC}"
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    echo -e "${GREEN}✅ Python environment setup complete${NC}"
fi

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${BLUE}Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
    echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
fi

# Function to start backend
start_backend() {
    echo -e "${BLUE}Starting FastAPI backend on port 8000...${NC}"
    cd backend
    source venv/bin/activate
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  .env file not found. Please create one based on .env.example${NC}"
        echo "Creating basic .env file with defaults..."
        cat > .env << EOL
DATABASE_URL=postgresql://opal:opal123@localhost:5432/opal_db
ASYNC_DATABASE_URL=postgresql+asyncpg://opal:opal123@localhost:5432/opal_db
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=opal_chunks
OPENAI_API_KEY=your_openai_api_key_here
CLERK_SECRET_KEY=your_clerk_secret_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_SERVICE_KEY=your_supabase_service_key_here
AVALANCHE_RPC=https://api.avax-test.network/ext/bc/C/rpc
SECRET_KEY=your-secret-key-for-encryption
ENVIRONMENT=development
DEBUG=true
EOL
        echo -e "${YELLOW}⚠️  Please update the .env file with your actual API keys${NC}"
    fi
    
    # Run database migrations
    echo -e "${BLUE}Running database migrations...${NC}"
    alembic upgrade head
    
    # Start the backend server
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    cd ..
}

# Function to start frontend
start_frontend() {
    echo -e "${BLUE}Starting Next.js frontend on port 3000...${NC}"
    cd frontend
    
    # Check if .env.local file exists
    if [ ! -f ".env.local" ]; then
        echo -e "${YELLOW}⚠️  .env.local file not found. Creating basic config...${NC}"
        cat > .env.local << EOL
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here
CLERK_SECRET_KEY=your_clerk_secret_key_here
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
NEXT_PUBLIC_APP_NAME=OPAL
EOL
        echo -e "${YELLOW}⚠️  Please update the .env.local file with your Clerk keys${NC}"
    fi
    
    npm run dev &
    FRONTEND_PID=$!
    cd ..
}

# Check if ports are already in use
if port_in_use 8000; then
    echo -e "${YELLOW}⚠️  Port 8000 is already in use. Backend may already be running.${NC}"
else
    start_backend
fi

if port_in_use 3000; then
    echo -e "${YELLOW}⚠️  Port 3000 is already in use. Frontend may already be running.${NC}"
else
    start_frontend
fi

# Wait a bit for services to start
sleep 5

echo ""
echo -e "${GREEN}🎉 OPAL is starting up!${NC}"
echo ""
echo -e "${BLUE}Services:${NC}"
echo "  📊 Frontend:  http://localhost:3000"
echo "  🚀 Backend:   http://localhost:8000"
echo "  📖 API Docs: http://localhost:8000/docs"
echo "  🔍 Qdrant:   http://localhost:6333"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Update .env files with your API keys"
echo "  2. Visit http://localhost:3000 to use OPAL"
echo "  3. Create a Clerk account and add your keys"
echo "  4. Add your OpenAI API key for AI features"
echo "  5. Set up Supabase for document storage"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "${BLUE}Shutting down services...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    echo -e "${GREEN}✅ All services stopped${NC}"
}

# Set up signal handling
trap cleanup EXIT INT TERM

# Wait for user interrupt
wait
