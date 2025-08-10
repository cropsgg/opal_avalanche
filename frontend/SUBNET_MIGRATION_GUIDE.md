# OPAL Frontend - Subnet Migration Guide

This guide explains the frontend changes made to support OPAL Phase 2 private Avalanche Subnet.

## Overview of Changes

The frontend has been updated to support both the new private Avalanche Subnet and legacy Fuji testnet, with a preference for the private subnet.

## New Features

### 1. Network Configuration System
- **File**: `lib/config.ts`
- **Purpose**: Centralized network management
- **Features**:
  - Multiple network support (private subnet, Fuji, local)
  - Dynamic network switching
  - Contract address management
  - Gas estimation for different networks

### 2. Enhanced Notarization Component
- **File**: `components/matters/NotarizationV2.tsx`
- **Purpose**: Advanced blockchain verification with subnet support
- **Features**:
  - Private vs public network selection
  - Network status checking
  - VPN requirement warnings
  - Enhanced security information display
  - Real-time network monitoring

### 3. Network Status Indicator
- **File**: `components/ui/network-status.tsx`
- **Purpose**: Real-time network status in header
- **Features**:
  - Current network display
  - Connection status
  - Health monitoring
  - Security warnings
  - VPN requirement alerts

## Updated Components

### MatterWorkspace.tsx
- Updated to use `NotarizationV2` instead of legacy `Notarization`
- Enhanced error handling for network issues

### Header.tsx
- Added `NetworkStatus` component for authenticated users
- Real-time network information in the header

### API Client (lib/api.ts)
- Updated notarization endpoints to support subnet routes
- Enhanced response types with subnet metadata
- Backward compatibility with legacy endpoints

### Types (types/index.ts)
- Extended `NotarizationProof` interface with subnet-specific fields
- Added network metadata and privacy indicators

## Configuration

### Environment Variables
Create `.env.local` from `env.example`:

```bash
# Network Selection
NEXT_PUBLIC_NETWORK=opal_production

# Contract Addresses (populated after deployment)
NEXT_PUBLIC_NOTARY_CONTRACT_ADDRESS=0x...
NEXT_PUBLIC_COMMIT_STORE_ADDRESS=0x...
NEXT_PUBLIC_PROJECT_REGISTRY_ADDRESS=0x...

# Feature Flags
NEXT_PUBLIC_ENABLE_PRIVATE_SUBNET=true
NEXT_PUBLIC_REQUIRE_VPN_WARNING=true
```

### Network Options
1. **opal_production** - Private subnet (default)
2. **avalanche_fuji** - Legacy Fuji testnet
3. **local** - Local development

## User Experience Changes

### For Legal Professionals

#### Private Subnet Benefits
- **Enhanced Privacy**: No public visibility of transactions
- **Lower Costs**: Optimized gas fees (~$0.001 per notarization)
- **Faster Finality**: ~6 second confirmation times
- **Professional Security**: Enterprise-grade key management

#### Network Selection
Users can choose between:
1. **Private Subnet** (Recommended)
   - Maximum privacy and security
   - VPN access required
   - Enterprise-grade infrastructure
   
2. **Public Network** (Legacy)
   - Publicly visible transactions
   - Higher gas costs
   - Deprecated (Phase 1)

### Visual Indicators

#### Network Status Badge
- **Green**: Connected to correct network, healthy
- **Yellow**: Connected but degraded performance
- **Red**: Wrong network or connection issues
- **Gray**: Not connected

#### Privacy Indicators
- **🔒 Lock Icon**: Private subnet (secure)
- **🌐 Globe Icon**: Public network (visible)
- **⚠️ Warning**: VPN required or network mismatch

## Migration Steps

### For Development

1. **Update Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure Environment**
   ```bash
   cp env.example .env.local
   # Edit .env.local with your values
   ```

3. **Test Network Switching**
   - Connect MetaMask to different networks
   - Verify network status component updates
   - Test notarization on both networks

### For Production

1. **Deploy with Subnet Configuration**
   ```bash
   # Set environment variables
   export NEXT_PUBLIC_NETWORK=opal_production
   export NEXT_PUBLIC_NOTARY_CONTRACT_ADDRESS=0x...
   
   # Build and deploy
   npm run build
   npm start
   ```

2. **Configure VPN Access**
   - Ensure users have VPN access to private subnet
   - Update documentation for VPN requirements
   - Test private subnet connectivity

## Backward Compatibility

The frontend maintains backward compatibility:

- **Legacy Notarization**: Old `Notarization` component still works
- **API Compatibility**: Both `/v1/notarize` and `/v1/subnet-notarize` supported
- **Gradual Migration**: Can switch networks without breaking existing functionality

## Testing

### Network Switching
1. Connect MetaMask
2. Switch between networks in wallet
3. Verify frontend updates automatically
4. Test notarization on each network

### Private Subnet
1. Ensure VPN connection (for production)
2. Switch to OPAL Private Subnet (Chain ID: 43210)
3. Test notarization flow
4. Verify privacy indicators

### Legacy Support
1. Switch to Avalanche Fuji (Chain ID: 43113)
2. Test legacy notarization
3. Verify deprecated warnings

## Security Considerations

### Private Subnet
- **VPN Required**: All private subnet access requires VPN
- **No Public Explorer**: Transactions not visible on public explorers
- **Enhanced Privacy**: Audit data encrypted, only hashes on-chain

### Public Network
- **Transparent**: All transactions publicly visible
- **Higher Risk**: Research content potentially exposed
- **Deprecated**: Recommend migration to private subnet

## Troubleshooting

### Network Connection Issues
1. Check VPN connection for private subnet
2. Verify wallet network settings
3. Try network switching in MetaMask
4. Check network status in header

### Contract Interaction Failures
1. Verify correct network selected
2. Check gas limits and balances
3. Ensure contract addresses are configured
4. Check VPN connectivity for private subnet

### MetaMask Issues
1. Reset MetaMask connection
2. Clear browser cache
3. Re-add OPAL network to MetaMask
4. Check custom RPC configuration

## Support

### Development Issues
- Check browser console for errors
- Verify environment variables
- Test with different wallets
- Try local development network

### Production Issues
- Verify VPN connectivity
- Check contract deployment status
- Validate network configuration
- Contact technical support

---

**🎉 Frontend successfully updated for OPAL Phase 2 private subnet!**

Users now have access to enhanced privacy, security, and performance through the private Avalanche Subnet while maintaining backward compatibility with existing systems.
