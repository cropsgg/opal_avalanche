# OPAL Server

Blockchain and Vector Database Server for OPAL (Open-Source Private AI for Law)

## Overview

The OPAL Server is a comprehensive service focused on:

- **Document Notarization**: Cryptographic integrity proofs for legal documents
- **Blockchain Operations**: Subnet notarization, contract interactions, and gas fee management
- **Vector Database**: Qdrant search for legal document retrieval
- **Encrypted Audit Trails**: Secure storage of document processing history

## Project Structure

```
Server/
├── backend/              # FastAPI backend service
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── blockchain/   # Subnet client & crypto
│   │   ├── config/       # Settings & configuration
│   │   └── storage/      # Qdrant & embedding
│   ├── scripts/          # Deployment & utility scripts
│   └── requirements.txt
├── frontend/             # Next.js dashboard
│   ├── app/              # App Router pages
│   ├── components/       # UI components
│   ├── lib/              # API client & utilities
│   └── types/            # TypeScript types
├── contracts/            # Smart contract ABIs
└── production-setup/     # Production deployment
```

## Features

### Document Management
- **Multi-document Upload**: Support for text files, manual entry
- **Content Preview**: Character count, content validation
- **Hash Generation**: Keccak-256 hashing with Merkle tree computation
- **Gas Estimation**: Preview costs before notarization

### Blockchain Operations
- **Subnet Notarization**: Publish Merkle roots to private Avalanche subnet
- **Encrypted Audit Storage**: AES-GCM encrypted audit data on-chain
- **Gas Fee Coverage**: Server pays all blockchain transaction costs
- **Contract Interactions**: Notary, CommitStore, and ProjectRegistry contracts

### Vector Database
- **Legal Document Search**: Semantic search through Qdrant
- **Evidence Retrieval**: Find relevant legal authorities and precedents
- **Filtered Search**: Court, date, and statute-based filtering

### Dashboard Features
- **Workflow Guidance**: Step-by-step document notarization process
- **Real-time Status**: Blockchain connectivity and system health
- **Result Verification**: Look up and verify existing notarizations
- **Audit Trail Access**: View encrypted audit data (when available)

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Qdrant vector database
- Private Avalanche subnet (optional for development)
- OpenAI API key for embeddings

### Installation

1. **Backend Setup**:
```bash
cd Server/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Frontend Setup**:
```bash
cd Server/frontend
npm install
```

3. **Configuration**:
```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration

# Frontend
cp frontend/.env.example frontend/.env.local
# Set SERVER_API_URL if different from default
```

4. **Start Development**:
```bash
# Start both backend and frontend
./start-all.sh

# Or start individually:
# Backend: cd backend && python start.py
# Frontend: cd frontend && npm run dev
```

The application will be available at:
- **Frontend Dashboard**: http://localhost:3001
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

## API Endpoints

### Document Operations
- `POST /api/v1/documents/hash` - Hash documents and compute Merkle root
- `POST /api/v1/subnet/notarize` - Notarize documents on subnet

### Blockchain Operations
- `GET /api/v1/subnet/notary/{run_id}` - Get notarization proof
- `GET /api/v1/subnet/audit/{run_id}` - Get encrypted audit data
- `GET /api/v1/status` - Blockchain status and connectivity

### Vector Search
- `POST /api/v1/search` - Semantic search through legal documents

### System Health
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed system status
- `GET /metrics` - System metrics

## Configuration

### Environment Variables

#### Backend (`backend/.env`)
```env
# Qdrant Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_api_key

# OpenAI (for embeddings)
OPENAI_API_KEY=your_openai_key

# Private Avalanche Subnet
SUBNET_RPC=http://your-subnet:9650/ext/bc/C/rpc
SUBNET_CHAIN_ID=43210
SUBNET_NOTARY_ADDR=0x...
SUBNET_COMMIT_ADDR=0x...
SUBNET_REGISTRY_ADDR=0x...
SUBNET_SENDER_PK=0x...

# Encryption
SUBNET_MASTER_KEY_B64=base64_encoded_key
FHE_SALT_OR_LABEL_SALT_BASE64=base64_encoded_salt

# Server
HOST=0.0.0.0
PORT=8001
DEBUG=false
LOG_LEVEL=INFO
```

#### Frontend (`frontend/.env.local`)
```env
SERVER_API_URL=http://localhost:8001
```

## Gas Fee Management

The server handles all blockchain gas fees automatically:

- **Transparent Costs**: Users see estimated costs before notarization
- **Server Payment**: All gas fees are paid by the server
- **Dynamic Pricing**: Gas estimates based on current network conditions
- **Cost Tracking**: Detailed gas usage reported for each operation

### Gas Estimation
- **Notary Operations**: ~50,000 gas (base cost)
- **Audit Commits**: ~100,000 + 20,000/KB gas
- **Current Gas Price**: 25 Gwei (configurable)

## Security Features

### Cryptographic Integrity
- **Keccak-256 Hashing**: Ethereum-standard document hashing
- **Merkle Trees**: Tamper-evident proof structures
- **Immutable Records**: Blockchain-based permanent storage

### Encryption
- **AES-GCM**: Authenticated encryption for audit data
- **Key Derivation**: Context-specific encryption keys
- **Opaque Labels**: Hidden metadata keys for privacy

### Access Control
- **Private Subnet**: Restricted network access
- **API Authentication**: (Configure for production)
- **Audit Trails**: Complete operation logging

## Development

### Adding New Features

1. **Backend**: Add endpoints in `backend/app/api/`
2. **Frontend**: Create components in `frontend/components/`
3. **Types**: Update `frontend/types/index.ts`
4. **API Client**: Update `frontend/lib/api.ts`

### Testing

```bash
# Backend tests
cd backend && python -m pytest

# Frontend linting
cd frontend && npm run lint
```

### Contract Deployment

Smart contracts are in `contracts/` with deployment scripts:

```bash
cd contracts
npm install
npx hardhat deploy --network subnet
```

## Production Deployment

See `production-setup/` for:
- Docker configurations
- Kubernetes manifests
- Subnet deployment scripts
- Monitoring setup

### Docker Deployment

```bash
# Build and run
docker-compose -f production-setup/docker-compose.yml up -d
```

## Monitoring

The application provides comprehensive monitoring:

- **Health Endpoints**: System and dependency status
- **Metrics**: Performance and usage statistics
- **Structured Logging**: JSON-formatted logs for analysis
- **Error Tracking**: Detailed error reporting

## Troubleshooting

### Common Issues

1. **Backend fails to start**:
   - Check Python version (3.11+ required)
   - Verify environment variables in `backend/.env`
   - Check port 8001 availability

2. **Frontend cannot connect to backend**:
   - Verify `SERVER_API_URL` in frontend config
   - Check CORS settings in backend
   - Ensure backend is running on correct port

3. **Blockchain operations fail**:
   - Verify subnet RPC connectivity
   - Check private key and contract addresses
   - Ensure sufficient balance for gas fees

4. **Vector search issues**:
   - Verify Qdrant connection
   - Check OpenAI API key
   - Ensure collection exists and has data

### Logs

- **Backend logs**: JSON-formatted via structlog
- **Frontend logs**: Browser console and Next.js logs
- **Production**: Configure log aggregation service

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Submit a pull request

## License

[Your License Here]