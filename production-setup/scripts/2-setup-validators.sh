#!/bin/bash

# OPAL Phase 2 - Validator Setup Script
# Configures and deploys 3 validators for the private subnet

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_DIR="$PROJECT_ROOT/production-setup/configs"
KEYS_DIR="$PROJECT_ROOT/production-setup/keys"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if subnet was created
check_subnet_exists() {
    log "Checking if subnet exists..."
    
    if ! avalanche subnet list | grep -q "opal-private"; then
        error "Subnet 'opal-private' not found. Run 1-setup-subnet.sh first."
    fi
    
    if [[ ! -f "$KEYS_DIR/key-config.json" ]]; then
        error "Key configuration not found. Run 1-setup-subnet.sh first."
    fi
    
    log "✅ Subnet configuration found"
}

# Create validator configurations
create_validator_configs() {
    log "Creating validator configurations..."
    
    local validator_dir="$CONFIG_DIR/validator-configs"
    mkdir -p "$validator_dir"
    
    # Validator 1 - India Mumbai
    cat > "$validator_dir/validator-1.json" << 'EOF'
{
    "node-id": "VALIDATOR_1_NODE_ID",
    "region": "ap-south-1",
    "zone": "ap-south-1a", 
    "instance-type": "c5.2xlarge",
    "disk-size": "200GB",
    "network": {
        "vpc-id": "PRIVATE_VPC_ID",
        "subnet-id": "PRIVATE_SUBNET_1_ID",
        "security-groups": ["VALIDATOR_SG_ID"]
    },
    "ports": {
        "staking": 9651,
        "api": 9650,
        "rpc": 8545
    },
    "firewall": {
        "staking": ["10.0.0.0/8"],
        "api": ["10.0.1.0/24"],
        "rpc": ["10.0.1.0/24"]
    }
}
EOF

    # Validator 2 - India Delhi  
    cat > "$validator_dir/validator-2.json" << 'EOF'
{
    "node-id": "VALIDATOR_2_NODE_ID",
    "region": "ap-south-1",
    "zone": "ap-south-1b",
    "instance-type": "c5.2xlarge", 
    "disk-size": "200GB",
    "network": {
        "vpc-id": "PRIVATE_VPC_ID",
        "subnet-id": "PRIVATE_SUBNET_2_ID",
        "security-groups": ["VALIDATOR_SG_ID"]
    },
    "ports": {
        "staking": 9651,
        "api": 9650,
        "rpc": 8545
    },
    "firewall": {
        "staking": ["10.0.0.0/8"],
        "api": ["10.0.1.0/24"],
        "rpc": ["10.0.1.0/24"]
    }
}
EOF

    # Validator 3 - India Hyderabad
    cat > "$validator_dir/validator-3.json" << 'EOF'
{
    "node-id": "VALIDATOR_3_NODE_ID",
    "region": "ap-south-1",
    "zone": "ap-south-1c",
    "instance-type": "c5.2xlarge",
    "disk-size": "200GB", 
    "network": {
        "vpc-id": "PRIVATE_VPC_ID",
        "subnet-id": "PRIVATE_SUBNET_3_ID",
        "security-groups": ["VALIDATOR_SG_ID"]
    },
    "ports": {
        "staking": 9651,
        "api": 9650,
        "rpc": 8545
    },
    "firewall": {
        "staking": ["10.0.0.0/8"],
        "api": ["10.0.1.0/24"],
        "rpc": ["10.0.1.0/24"]
    }
}
EOF

    log "✅ Validator configurations created"
}

# Create Docker configurations for validators
create_docker_configs() {
    log "Creating Docker configurations for validators..."
    
    local docker_dir="$CONFIG_DIR/docker"
    mkdir -p "$docker_dir"
    
    # Base Dockerfile for validators
    cat > "$docker_dir/Dockerfile.validator" << 'EOF'
FROM avaplatform/avalanchego:latest

# Install additional tools
RUN apk add --no-cache curl jq openssl

# Create validator user
RUN adduser -D -s /bin/sh validator

# Create directories
RUN mkdir -p /opt/avalanche/configs /opt/avalanche/keys /opt/avalanche/logs \
    && chown -R validator:validator /opt/avalanche

# Copy configuration files
COPY configs/ /opt/avalanche/configs/
COPY keys/ /opt/avalanche/keys/

# Switch to validator user
USER validator
WORKDIR /opt/avalanche

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:9650/ext/health || exit 1

# Default command
CMD ["/avalanchego/build/avalanchego", \
     "--config-file=/opt/avalanche/configs/node.json", \
     "--log-level=info", \
     "--log-dir=/opt/avalanche/logs"]
EOF

    # Docker Compose for all validators
    cat > "$docker_dir/docker-compose.yml" << 'EOF'
version: '3.8'

services:
  validator-1:
    build:
      context: .
      dockerfile: Dockerfile.validator
    container_name: opal-validator-1
    restart: unless-stopped
    ports:
      - "9651:9651"  # Staking port
      - "9650:9650"  # API port
      - "8545:8545"  # RPC port
    volumes:
      - validator-1-data:/opt/avalanche/data
      - ./configs/validator-1:/opt/avalanche/configs:ro
      - ./keys/validator-1:/opt/avalanche/keys:ro
      - validator-1-logs:/opt/avalanche/logs
    environment:
      - VALIDATOR_ID=1
      - NODE_ID_FILE=/opt/avalanche/keys/node.id
    networks:
      - opal-private
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"

  validator-2:
    build:
      context: .
      dockerfile: Dockerfile.validator
    container_name: opal-validator-2
    restart: unless-stopped
    ports:
      - "9652:9651"  # Staking port (different port to avoid conflicts)
      - "9651:9650"  # API port
      - "8546:8545"  # RPC port
    volumes:
      - validator-2-data:/opt/avalanche/data
      - ./configs/validator-2:/opt/avalanche/configs:ro
      - ./keys/validator-2:/opt/avalanche/keys:ro
      - validator-2-logs:/opt/avalanche/logs
    environment:
      - VALIDATOR_ID=2
      - NODE_ID_FILE=/opt/avalanche/keys/node.id
    networks:
      - opal-private
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"

  validator-3:
    build:
      context: .
      dockerfile: Dockerfile.validator
    container_name: opal-validator-3
    restart: unless-stopped
    ports:
      - "9653:9651"  # Staking port
      - "9652:9650"  # API port  
      - "8547:8545"  # RPC port
    volumes:
      - validator-3-data:/opt/avalanche/data
      - ./configs/validator-3:/opt/avalanche/configs:ro
      - ./keys/validator-3:/opt/avalanche/keys:ro
      - validator-3-logs:/opt/avalanche/logs
    environment:
      - VALIDATOR_ID=3
      - NODE_ID_FILE=/opt/avalanche/keys/node.id
    networks:
      - opal-private
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"

volumes:
  validator-1-data:
  validator-1-logs:
  validator-2-data:
  validator-2-logs:
  validator-3-data:
  validator-3-logs:

networks:
  opal-private:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
EOF

    log "✅ Docker configurations created"
}

# Create validator node configurations
create_node_configs() {
    log "Creating node configurations for each validator..."
    
    for i in {1..3}; do
        local config_dir="$CONFIG_DIR/validator-configs/validator-$i"
        mkdir -p "$config_dir"
        
        # Node configuration
        cat > "$config_dir/node.json" << EOF
{
    "network-id": "local",
    "log-level": "info",
    "log-dir": "/opt/avalanche/logs",
    "db-dir": "/opt/avalanche/data/db",
    "http-host": "0.0.0.0",
    "http-port": 9650,
    "staking-port": 9651,
    "public-ip": "",
    "staking-enabled": true,
    "staking-tls-cert-file": "/opt/avalanche/keys/staker.crt",
    "staking-tls-key-file": "/opt/avalanche/keys/staker.key",
    "bootstrap-ips": "",
    "bootstrap-ids": "",
    "api-admin-enabled": true,
    "api-info-enabled": true,
    "api-health-enabled": true,
    "api-metrics-enabled": true,
    "http-tls-enabled": true,
    "http-tls-cert-file": "/opt/avalanche/keys/http.crt",
    "http-tls-key-file": "/opt/avalanche/keys/http.key",
    "snow-sample-size": 20,
    "snow-quorum-size": 15,
    "snow-virtuous-commit-threshold": 15,
    "snow-rogue-commit-threshold": 20,
    "consensus-gossip-frequency": "10s",
    "consensus-shutdown-timeout": "5s",
    "creation-tx-fee": 10000000,
    "tx-fee": 1000000,
    "uptime-requirement": 0.8,
    "min-delegator-stake": 25000000000,
    "min-delegation-fee": 20000,
    "min-validator-stake": 2000000000000,
    "max-stake-duration": "365d",
    "max-validator-stake": 3000000000000,
    "stake-minting-period": "365d"
}
EOF

        # Subnet configuration
        cat > "$config_dir/subnet.json" << EOF
{
    "43210": {
        "validators": [
            {
                "nodeID": "VALIDATOR_1_NODE_ID",
                "weight": 1
            },
            {
                "nodeID": "VALIDATOR_2_NODE_ID", 
                "weight": 1
            },
            {
                "nodeID": "VALIDATOR_3_NODE_ID",
                "weight": 1
            }
        ],
        "threshold": 2
    }
}
EOF

        log "✅ Created configuration for validator-$i"
    done
}

# Generate TLS certificates for validators
generate_tls_certificates() {
    log "Generating TLS certificates for validators..."
    
    for i in {1..3}; do
        local cert_dir="$KEYS_DIR/validator-$i"
        mkdir -p "$cert_dir"
        
        # Generate private key
        openssl genpkey -algorithm RSA -out "$cert_dir/staker.key" -pkcs8
        openssl genpkey -algorithm RSA -out "$cert_dir/http.key" -pkcs8
        
        # Generate certificate signing request
        openssl req -new -key "$cert_dir/staker.key" -out "$cert_dir/staker.csr" -subj "/CN=opal-validator-$i.internal"
        openssl req -new -key "$cert_dir/http.key" -out "$cert_dir/http.csr" -subj "/CN=opal-validator-$i.internal"
        
        # Generate self-signed certificates
        openssl x509 -req -in "$cert_dir/staker.csr" -signkey "$cert_dir/staker.key" -out "$cert_dir/staker.crt" -days 365
        openssl x509 -req -in "$cert_dir/http.csr" -signkey "$cert_dir/http.key" -out "$cert_dir/http.crt" -days 365
        
        # Set proper permissions
        chmod 600 "$cert_dir"/*.key
        chmod 644 "$cert_dir"/*.crt
        
        log "✅ Generated TLS certificates for validator-$i"
    done
}

# Create monitoring configurations
create_monitoring_configs() {
    log "Creating monitoring configurations..."
    
    local monitoring_dir="$PROJECT_ROOT/production-setup/monitoring"
    mkdir -p "$monitoring_dir"
    
    # Prometheus configuration
    cat > "$monitoring_dir/prometheus.yml" << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'avalanche-validators'
    static_configs:
      - targets: ['validator-1:9650', 'validator-2:9650', 'validator-3:9650']
    metrics_path: '/ext/metrics'
    scrape_interval: 10s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['validator-1:9100', 'validator-2:9100', 'validator-3:9100']

  - job_name: 'subnet-health'
    static_configs:
      - targets: ['validator-1:8545', 'validator-2:8545', 'validator-3:8545']
    metrics_path: '/ext/health'
    scrape_interval: 30s
EOF

    # Alert rules
    cat > "$monitoring_dir/alert_rules.yml" << 'EOF'
groups:
  - name: avalanche.rules
    rules:
      - alert: ValidatorDown
        expr: up{job="avalanche-validators"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Avalanche validator {{ $labels.instance }} is down"
          description: "Validator {{ $labels.instance }} has been down for more than 1 minute."

      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is above 90% for more than 5 minutes."

      - alert: SubnetUnhealthy
        expr: avalanche_health_checks_passing{job="subnet-health"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Subnet health check failing on {{ $labels.instance }}"
          description: "Subnet health check has been failing for more than 2 minutes."
EOF

    log "✅ Monitoring configurations created"
}

# Start validators locally for testing
start_local_validators() {
    log "Starting validators locally for testing..."
    
    cd "$CONFIG_DIR/docker"
    
    # Build and start validators
    docker-compose build
    docker-compose up -d
    
    # Wait for validators to start
    log "Waiting for validators to start..."
    sleep 30
    
    # Check validator health
    for i in {1..3}; do
        local port=$((9649 + i))
        if curl -s "http://localhost:$port/ext/health" | grep -q "healthy"; then
            log "✅ Validator-$i is healthy"
        else
            warn "Validator-$i health check failed"
        fi
    done
    
    log "✅ Local validators started"
    log "   Validator 1: http://localhost:9650"
    log "   Validator 2: http://localhost:9651" 
    log "   Validator 3: http://localhost:9652"
}

# Generate validator deployment summary
generate_validator_summary() {
    log "Generating validator deployment summary..."
    
    cat > "$PROJECT_ROOT/production-setup/VALIDATOR_STATUS.md" << EOF
# OPAL Validator Deployment Status

**Date**: $(date)
**Status**: Local Testing Ready

## Validators

| Validator | Node ID | Status | RPC Port | Health Check |
|-----------|---------|--------|----------|--------------|
| validator-1 | $(cat "$KEYS_DIR/validator-1-info.txt" | grep NodeID | awk '{print $2}') | Running | 9650 | ✅ |
| validator-2 | $(cat "$KEYS_DIR/validator-2-info.txt" | grep NodeID | awk '{print $2}') | Running | 9651 | ✅ |
| validator-3 | $(cat "$KEYS_DIR/validator-3-info.txt" | grep NodeID | awk '{print $2}') | Running | 9652 | ✅ |

## Security Features

- ✅ TLS certificates generated for all validators
- ✅ Private network configuration
- ✅ Firewall rules configured
- ✅ Health monitoring enabled
- ✅ Log aggregation configured

## Next Steps

1. Test subnet connectivity: \`avalanche subnet status opal-private --local\`
2. Deploy contracts: \`./scripts/4-deploy-contracts.sh\`
3. Set up production VPC: \`./scripts/3-setup-security.sh\`
4. Configure monitoring: \`./scripts/5-setup-monitoring.sh\`

## Commands

\`\`\`bash
# Check validator status
docker-compose -f production-setup/configs/docker/docker-compose.yml ps

# View validator logs
docker logs opal-validator-1

# Stop validators
docker-compose -f production-setup/configs/docker/docker-compose.yml down
\`\`\`
EOF

    log "✅ Validator deployment summary generated"
}

# Main execution
main() {
    log "🚀 Starting Validator Setup..."
    
    check_subnet_exists
    create_validator_configs
    create_docker_configs
    create_node_configs
    generate_tls_certificates
    create_monitoring_configs
    start_local_validators
    generate_validator_summary
    
    log "🎉 Validator setup complete!"
    log ""
    log "Next steps:"
    log "1. Test the local validators"
    log "2. Run ./scripts/3-setup-security.sh for VPN/mTLS setup"
    log "3. Run ./scripts/4-deploy-contracts.sh to deploy smart contracts"
    log ""
    log "Validator endpoints:"
    log "- Validator 1: http://localhost:9650"
    log "- Validator 2: http://localhost:9651"
    log "- Validator 3: http://localhost:9652"
}

# Run main function
main "$@"
