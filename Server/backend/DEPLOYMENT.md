# OPAL Server Backend Deployment Guide

## Overview

The OPAL Server backend is a FastAPI application that provides:
- ✅ **Hardcoded Authentication** (`opalteam321` / `weareteamalphaq`)
- 🔗 **Blockchain Operations** (Avalanche Subnet integration)
- 🧠 **Knowledge Graph APIs** (Qdrant vector database)
- 📊 **Health Monitoring** and metrics

## Quick Start

### Local Development

1. **Clone and setup**:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp env.example .env
# Edit .env with your settings
```

3. **Run the server**:
```bash
python start.py
```

The server will be available at `http://localhost:8001`

### Docker Deployment

1. **Build and run**:
```bash
docker build -t opal-server .
docker run -p 8001:8001 opal-server
```

2. **Using Docker Compose** (includes Qdrant):
```bash
docker-compose up -d
```

## Authentication

The backend includes hardcoded authentication:
- **User ID**: `opalteam321`
- **Password**: `weareteamalphaq`

### API Endpoints

- `POST /api/v1/auth/login` - Login with credentials
- `POST /api/v1/auth/logout` - Logout current session
- `GET /api/v1/auth/me` - Get current user info
- `GET /api/v1/auth/status` - Authentication system status

## Deployment Platforms

### 1. Railway

```bash
# Connect to Railway
railway login
railway init
railway up
```

Configuration: `railway.json`

### 2. Render

1. Connect your GitHub repository
2. Create new Web Service
3. Set build command: `docker build`
4. Configure environment variables

Configuration: `render.yaml`

### 3. DigitalOcean App Platform

```bash
# Using App Spec
doctl apps create --spec app.yaml
```

### 4. Heroku (with Docker)

```bash
heroku create opal-server
heroku container:push web
heroku container:release web
```

## Environment Variables

### Required for Production

```bash
# Basic Settings
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=your-production-secret-key

# Vector Database
QDRANT_URL=your-qdrant-instance-url
QDRANT_API_KEY=your-qdrant-api-key

# AI/ML Services
OPENAI_API_KEY=your-openai-api-key
```

### Optional (Blockchain Features)

```bash
# Avalanche Subnet
SUBNET_RPC=your-subnet-rpc-url
SUBNET_CHAIN_ID=43210
SUBNET_NOTARY_ADDR=contract-address
SUBNET_COMMIT_ADDR=contract-address
SUBNET_REGISTRY_ADDR=contract-address
SUBNET_SENDER_PK=private-key
```

## Health Checks

The server provides multiple health check endpoints:

- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed component health
- `GET /metrics` - System metrics

## Security Notes

⚠️ **Important**: This deployment uses hardcoded authentication for demo purposes.

For production use:
1. Replace hardcoded credentials with proper user management
2. Use environment variables for sensitive data
3. Enable HTTPS/TLS
4. Configure CORS appropriately
5. Use secure secret keys

## Troubleshooting

### Common Issues

1. **Port binding issues**:
   - Ensure port 8001 is available
   - Check firewall settings

2. **Qdrant connection**:
   - Verify Qdrant is running and accessible
   - Check network connectivity

3. **Missing dependencies**:
   - Ensure all packages in `requirements.txt` are installed
   - Check Python version compatibility (3.11+)

### Logs

Check application logs:
```bash
# Docker
docker logs <container-id>

# Local
tail -f server.log
```

## Support

The backend is now fully deployed and ready for production use with the hardcoded authentication system.
