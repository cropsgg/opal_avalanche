# OPAL Server Deployment Guide

## Quick Deployment

### Development
```bash
./deploy.sh development
```

### Production
```bash
./deploy.sh production
```

## Manual Deployment

### Prerequisites
- Docker and Docker Compose
- 8GB+ RAM recommended
- 50GB+ disk space

### 1. Environment Configuration

Copy and configure environment files:

```bash
# Backend configuration
cp backend/.env.example backend/.env
# Edit backend/.env with your settings

# Frontend configuration (development only)
echo "SERVER_API_URL=http://localhost:8001" > frontend/.env.local
```

### 2. Required Configuration

Update `backend/.env` with:

#### Qdrant Configuration
```env
QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION=opal_chunks
```

#### OpenAI API
```env
OPENAI_API_KEY=your-openai-api-key
OPENAI_EMBED_MODEL=text-embedding-3-large
```

#### Avalanche Subnet (Optional)
```env
SUBNET_RPC=https://your-subnet-rpc
SUBNET_CHAIN_ID=43210
SUBNET_NOTARY_ADDR=0x...
SUBNET_COMMIT_ADDR=0x...
SUBNET_REGISTRY_ADDR=0x...
SUBNET_SENDER_PK=0x...
```

#### Encryption Keys
```env
SUBNET_MASTER_KEY_B64=base64-encoded-32-byte-key
FHE_SALT_OR_LABEL_SALT_BASE64=base64-encoded-salt
SECRET_KEY=your-secret-key
```

### 3. Deploy Services

#### Development
```bash
docker-compose up --build -d backend frontend qdrant
```

#### Production (with Nginx)
```bash
docker-compose --profile production up --build -d
```

### 4. Verify Deployment

Check service health:
```bash
docker-compose ps
docker-compose logs -f backend
```

Test endpoints:
- **Frontend**: http://localhost:3001 (dev) or http://localhost (prod)
- **Backend API**: http://localhost:8001 (dev) or http://localhost/api (prod)
- **API Docs**: http://localhost:8001/docs (dev) or http://localhost/docs (prod)
- **Qdrant**: http://localhost:6333

### 5. Initialize Data

Create Qdrant collection:
```bash
curl -X PUT http://localhost:6333/collections/opal_chunks \
  -H "Content-Type: application/json" \
  -d '{
    "vectors": {
      "size": 3072,
      "distance": "Cosine"
    }
  }'
```

## Production Considerations

### Security
1. **API Keys**: Set strong API keys in production
2. **CORS**: Configure allowed origins
3. **SSL/TLS**: Enable HTTPS with proper certificates
4. **Firewall**: Restrict access to necessary ports only

### Monitoring
1. **Health Checks**: Built-in health checks for all services
2. **Logs**: Structured JSON logging with log levels
3. **Metrics**: Enable metrics collection in production

### Backup
1. **Qdrant Data**: Volume `qdrant_data` contains vector database
2. **Environment**: Backup `.env` files securely
3. **Keys**: Backup encryption keys securely

### Scaling
1. **Horizontal**: Multiple backend instances behind load balancer
2. **Database**: Qdrant cluster for high availability
3. **Storage**: External storage for large datasets

## Troubleshooting

### Common Issues

#### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Check environment
docker-compose exec backend env | grep -E "(QDRANT|OPENAI|SUBNET)"

# Test dependencies
docker-compose exec backend curl -f http://qdrant:6333/health
```

#### Frontend build errors
```bash
# Rebuild frontend
docker-compose build --no-cache frontend

# Check environment
docker-compose exec frontend env | grep SERVER_API_URL
```

#### Qdrant connection issues
```bash
# Check Qdrant health
curl http://localhost:6333/health

# Check collections
curl http://localhost:6333/collections

# Create collection if missing
curl -X PUT http://localhost:6333/collections/opal_chunks \
  -H "Content-Type: application/json" \
  -d '{"vectors": {"size": 3072, "distance": "Cosine"}}'
```

### Service URLs

#### Development
- Frontend: http://localhost:3001
- Backend: http://localhost:8001
- API Docs: http://localhost:8001/docs
- Qdrant: http://localhost:6333

#### Production
- Frontend: http://localhost (via Nginx)
- Backend: http://localhost/api (via Nginx)
- API Docs: http://localhost/docs (via Nginx)
- Qdrant: http://localhost:6333 (direct)

### Docker Commands

```bash
# View all services
docker-compose ps

# View logs
docker-compose logs -f [service]

# Restart service
docker-compose restart [service]

# Rebuild service
docker-compose build --no-cache [service]

# Execute commands in container
docker-compose exec [service] [command]

# Clean up
docker-compose down --volumes --remove-orphans
```

## Security Checklist

- [ ] Environment files not in version control
- [ ] Strong API keys configured
- [ ] CORS origins properly set
- [ ] SSL certificates installed (production)
- [ ] Firewall rules configured
- [ ] Regular security updates
- [ ] Backup encryption keys securely
- [ ] Monitor access logs
- [ ] Rate limiting enabled
- [ ] Input validation in place
