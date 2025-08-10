#!/bin/bash

# OPAL Phase 2 - Private Subnet Setup Script
# Creates and deploys a private permissioned Avalanche Subnet for OPAL

set -e

echo "🚀 OPAL Phase 2 - Private Subnet Setup"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check dependencies
echo -e "\n${BLUE}🔧 Checking dependencies...${NC}"

if ! command -v avalanche &> /dev/null; then
    echo -e "${RED}❌ Avalanche CLI not found${NC}"
    echo "Please install Avalanche CLI first:"
    echo "curl -sSfL https://raw.githubusercontent.com/ava-labs/avalanche-cli/main/scripts/install.sh | sh -s"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found${NC}"
    echo "Please install Node.js first"
    exit 1
fi

echo -e "${GREEN}✅ Dependencies OK${NC}"

# Setup directories
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SUBNET_DIR="${PROJECT_ROOT}/subnet"
CONTRACTS_DIR="${PROJECT_ROOT}/subnet-contracts"

echo -e "\n${BLUE}📁 Project root: ${PROJECT_ROOT}${NC}"

# Step 1: Create Avalanche subnet
echo -e "\n${BLUE}⛓️  Step 1: Creating Avalanche Subnet...${NC}"

cd "${SUBNET_DIR}"

# Create subnet configuration if it doesn't exist
if [ ! -f "subnet-config.json" ]; then
    echo -e "${YELLOW}Creating subnet configuration...${NC}"
    cat > subnet-config.json << 'EOF'
{
  "vm": "Subnet-EVM",
  "subnet": {
    "name": "opal-private-subnet",
    "validators": 3
  },
  "chainConfig": {
    "chainId": 43210,
    "homesteadBlock": 0,
    "eip150Block": 0,
    "eip155Block": 0,
    "eip158Block": 0,
    "byzantiumBlock": 0,
    "constantinopleBlock": 0,
    "petersburgBlock": 0,
    "istanbulBlock": 0,
    "muirGlacierBlock": 0,
    "subnetEVMTimestamp": 0
  }
}
EOF
fi

# Create subnet using Avalanche CLI
echo -e "${YELLOW}Creating subnet with Avalanche CLI...${NC}"

# Check if subnet already exists
if avalanche subnet list | grep -q "opal-private-subnet"; then
    echo -e "${GREEN}✅ Subnet 'opal-private-subnet' already exists${NC}"
else
    echo -e "${YELLOW}Creating new subnet...${NC}"
    avalanche subnet create opal-private-subnet \
        --evm \
        --genesis genesis.json \
        --force
    echo -e "${GREEN}✅ Subnet created${NC}"
fi

# Step 2: Deploy subnet locally for testing
echo -e "\n${BLUE}🖥️  Step 2: Deploying subnet locally...${NC}"

echo -e "${YELLOW}Starting local subnet deployment...${NC}"
echo -e "${YELLOW}Note: This will run in the background${NC}"

# Deploy subnet (this will run the local network)
avalanche subnet deploy opal-private-subnet --local &
SUBNET_PID=$!

echo -e "${GREEN}✅ Subnet deployment started (PID: ${SUBNET_PID})${NC}"
echo -e "${YELLOW}Waiting for subnet to be ready...${NC}"
sleep 10

# Step 3: Install and compile contracts
echo -e "\n${BLUE}📝 Step 3: Installing and compiling contracts...${NC}"

cd "${CONTRACTS_DIR}"

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing contract dependencies...${NC}"
    npm install
fi

echo -e "${YELLOW}Compiling contracts...${NC}"
npm run compile

echo -e "${GREEN}✅ Contracts compiled${NC}"

# Step 4: Deploy contracts to subnet
echo -e "\n${BLUE}🚀 Step 4: Deploying contracts to subnet...${NC}"

echo -e "${YELLOW}Deploying contracts...${NC}"

# Set up environment for deployment
export SUBNET_RPC="http://localhost:9650/ext/bc/opal/rpc"
export SUBNET_CHAIN_ID="43210"

# Generate a test private key if not set
if [ -z "$SUBNET_SENDER_PK" ]; then
    echo -e "${YELLOW}Generating test private key...${NC}"
    # This is a well-known test key - DO NOT use in production
    export SUBNET_SENDER_PK="0x56289e99c94b6912bfc12adc093c9b51124f0dc54ac7a766b2bc5ccf558d8027"
    echo -e "${YELLOW}Using test private key (DO NOT use in production)${NC}"
fi

# Deploy contracts
npm run deploy:local

echo -e "${GREEN}✅ Contracts deployed${NC}"

# Step 5: Setup backend environment
echo -e "\n${BLUE}⚙️  Step 5: Setting up backend environment...${NC}"

BACKEND_ENV="${PROJECT_ROOT}/backend/.env"

# Read deployed contract addresses from deployment.json
DEPLOYMENT_FILE="${PROJECT_ROOT}/backend/app/subnet/deployment.json"

if [ -f "$DEPLOYMENT_FILE" ]; then
    NOTARY_ADDR=$(jq -r '.contracts.Notary.address' "$DEPLOYMENT_FILE")
    COMMIT_ADDR=$(jq -r '.contracts.CommitStore.address' "$DEPLOYMENT_FILE")  
    REGISTRY_ADDR=$(jq -r '.contracts.ProjectRegistry.address' "$DEPLOYMENT_FILE")
    
    echo -e "${YELLOW}Updating backend .env file...${NC}"
    
    # Create or update .env file
    if [ ! -f "$BACKEND_ENV" ]; then
        touch "$BACKEND_ENV"
    fi
    
    # Remove old subnet settings
    sed -i.bak '/^SUBNET_/d' "$BACKEND_ENV" 2>/dev/null || true
    
    # Add new subnet settings
    cat >> "$BACKEND_ENV" << EOF

# OPAL Phase 2 - Private Subnet Configuration
SUBNET_RPC=http://localhost:9650/ext/bc/opal/rpc
SUBNET_CHAIN_ID=43210
SUBNET_NOTARY_ADDR=${NOTARY_ADDR}
SUBNET_COMMIT_ADDR=${COMMIT_ADDR}
SUBNET_REGISTRY_ADDR=${REGISTRY_ADDR}
SUBNET_SENDER_PK=${SUBNET_SENDER_PK}

# Subnet Encryption (generate proper keys for production)
SUBNET_MASTER_KEY_B64=$(openssl rand -base64 32)
FHE_SALT_OR_LABEL_SALT_BASE64=$(openssl rand -base64 16)
EOF
    
    echo -e "${GREEN}✅ Backend environment configured${NC}"
    
    # Display configuration
    echo -e "\n${BLUE}📋 Subnet Configuration:${NC}"
    echo -e "   RPC: http://localhost:9650/ext/bc/opal/rpc"
    echo -e "   Chain ID: 43210"
    echo -e "   Notary: ${NOTARY_ADDR}"
    echo -e "   CommitStore: ${COMMIT_ADDR}"
    echo -e "   Registry: ${REGISTRY_ADDR}"
    
else
    echo -e "${RED}❌ Deployment file not found: ${DEPLOYMENT_FILE}${NC}"
    echo -e "${YELLOW}Contract deployment may have failed${NC}"
fi

# Step 6: Run demo
echo -e "\n${BLUE}🎬 Step 6: Running demo...${NC}"

cd "${PROJECT_ROOT}"

echo -e "${YELLOW}Running OPAL Phase 2 demo...${NC}"
python3 scripts/demo_run.py

# Summary
echo -e "\n${'=' * 50}"
echo -e "${GREEN}🎉 OPAL Phase 2 Setup Complete!${NC}"
echo -e "\n${BLUE}📋 What was created:${NC}"
echo -e "   • Private Avalanche Subnet (Chain ID: 43210)"
echo -e "   • Immutable smart contracts (Notary, CommitStore, Registry)" 
echo -e "   • Encrypted audit system with AES-GCM"
echo -e "   • Backend integration for subnet notarization"
echo -e "   • Demo script showing complete flow"

echo -e "\n${BLUE}🔧 Next steps:${NC}"
echo -e "   • Run 'python3 scripts/demo_run.py' to test the flow"
echo -e "   • Run 'python3 scripts/register_release.py' to register current version"
echo -e "   • Start backend: 'cd backend && uvicorn app.main:app --reload'"
echo -e "   • Test API: 'curl http://localhost:8000/health'"

echo -e "\n${BLUE}🛑 To stop the subnet:${NC}"
echo -e "   • Kill subnet process: kill ${SUBNET_PID}"
echo -e "   • Or use: avalanche network stop"

echo -e "\n${YELLOW}⚠️  Security Notes:${NC}"
echo -e "   • This setup uses test keys - NEVER use in production"
echo -e "   • Generate proper keys and store in KMS for production"
echo -e "   • Configure proper VPC/VPN access for private RPC"
echo -e "   • Use hardware security modules for validator keys"
