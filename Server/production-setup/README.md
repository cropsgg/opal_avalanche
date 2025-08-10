# OPAL Phase 2 - Production Subnet Deployment

This directory contains all the scripts and configuration needed to deploy the OPAL private Avalanche Subnet for production use.

## Overview

- **Private Subnet-EVM**: 3 validators, all operated by us
- **Chain ID**: 43210 (production)
- **Gas Token**: AVAX
- **Security**: VPN/VPC + mTLS, IP allowlist, HSM/KMS keys
- **Precompiles**: TxAllowList, ContractDeployerAllowList, FeeManager

## Directory Structure

```
production-setup/
├── configs/
│   ├── genesis.json          # Subnet genesis configuration
│   ├── subnet-config.json    # Avalanche CLI subnet config
│   └── validator-configs/    # Individual validator configurations
├── scripts/
│   ├── 1-setup-subnet.sh     # Create and configure subnet
│   ├── 2-setup-validators.sh # Deploy and start validators
│   ├── 3-setup-security.sh   # Configure VPN/mTLS
│   ├── 4-deploy-contracts.sh # Deploy smart contracts
│   └── 5-setup-monitoring.sh # Configure monitoring
├── terraform/               # Infrastructure as Code
├── keys/                   # Key management (KMS integration)
└── monitoring/             # Monitoring and alerting configs
```

## Deployment Steps

1. **Subnet Creation**: `./scripts/1-setup-subnet.sh`
2. **Validator Setup**: `./scripts/2-setup-validators.sh`
3. **Security Config**: `./scripts/3-setup-security.sh`
4. **Contract Deployment**: `./scripts/4-deploy-contracts.sh`
5. **Monitoring Setup**: `./scripts/5-setup-monitoring.sh`

## Prerequisites

- Avalanche CLI installed
- AWS CLI configured (for KMS)
- Terraform (for infrastructure)
- Docker (for validators)
- Valid AWS account with KMS permissions

## Security Considerations

- All private keys stored in AWS KMS
- Validators behind VPC with no public internet access
- RPC endpoints protected by mTLS and IP allowlist
- All communications encrypted
- Regular key rotation
- Comprehensive audit logging
