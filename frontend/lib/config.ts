// OPAL Phase 2 - Network Configuration
// Manages configuration for the private Avalanche Subnet

export interface NetworkConfig {
  id: number;
  name: string;
  displayName: string;
  rpcUrl: string;
  explorerUrl: string;
  nativeCurrency: {
    name: string;
    symbol: string;
    decimals: number;
  };
  isPrivate: boolean;
  requiresVPN: boolean;
}

export const NETWORKS: Record<string, NetworkConfig> = {
  // OPAL Private Subnet (Phase 2 Production)
  opal_production: {
    id: 43210,
    name: 'OPAL Private Subnet',
    displayName: 'OPAL Private Network',
    rpcUrl: 'https://opal-rpc.internal', // VPN-only access
    explorerUrl: '', // No public explorer for private subnet
    nativeCurrency: {
      name: 'Avalanche',
      symbol: 'AVAX',
      decimals: 18,
    },
    isPrivate: true,
    requiresVPN: true,
  },
  
  // Avalanche Fuji Testnet (Legacy/Development)
  avalanche_fuji: {
    id: 43113,
    name: 'Avalanche Fuji Testnet',
    displayName: 'Avalanche Fuji',
    rpcUrl: 'https://api.avax-test.network/ext/bc/C/rpc',
    explorerUrl: 'https://testnet.snowtrace.io',
    nativeCurrency: {
      name: 'Avalanche',
      symbol: 'AVAX',
      decimals: 18,
    },
    isPrivate: false,
    requiresVPN: false,
  },
  
  // Local Development
  local: {
    id: 31337,
    name: 'Local Hardhat',
    displayName: 'Local Development',
    rpcUrl: 'http://localhost:8545',
    explorerUrl: '',
    nativeCurrency: {
      name: 'Ethereum',
      symbol: 'ETH',
      decimals: 18,
    },
    isPrivate: false,
    requiresVPN: false,
  },
};

// Environment-based network selection
export function getCurrentNetwork(): NetworkConfig {
  const networkEnv = process.env.NEXT_PUBLIC_NETWORK || 'opal_production';
  
  // Default to production network
  return NETWORKS[networkEnv] || NETWORKS.opal_production;
}

// Check if user is connected to the correct network
export function isCorrectNetwork(userChainId: number): boolean {
  const currentNetwork = getCurrentNetwork();
  return userChainId === currentNetwork.id;
}

// Get network switching parameters for wallets
export function getNetworkSwitchParams(networkKey: string) {
  const network = NETWORKS[networkKey];
  if (!network) return null;
  
  return {
    chainId: `0x${network.id.toString(16)}`,
    chainName: network.displayName,
    nativeCurrency: network.nativeCurrency,
    rpcUrls: [network.rpcUrl],
    blockExplorerUrls: network.explorerUrl ? [network.explorerUrl] : [],
  };
}

// Contract addresses for different networks
export const CONTRACT_ADDRESSES: Record<string, {
  notary: string;
  commitStore: string;
  projectRegistry: string;
}> = {
  opal_production: {
    notary: process.env.NEXT_PUBLIC_NOTARY_CONTRACT_ADDRESS || '',
    commitStore: process.env.NEXT_PUBLIC_COMMIT_STORE_ADDRESS || '',
    projectRegistry: process.env.NEXT_PUBLIC_PROJECT_REGISTRY_ADDRESS || '',
  },
  avalanche_fuji: {
    notary: process.env.NEXT_PUBLIC_FUJI_NOTARY_ADDRESS || '',
    commitStore: process.env.NEXT_PUBLIC_FUJI_COMMIT_ADDRESS || '',
    projectRegistry: process.env.NEXT_PUBLIC_FUJI_REGISTRY_ADDRESS || '',
  },
  local: {
    notary: '0x5FbDB2315678afecb367f032d93F642f64180aa3',
    commitStore: '0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512',
    projectRegistry: '0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0',
  },
};

// Get contract addresses for current network
export function getContractAddresses() {
  const network = getCurrentNetwork();
  const networkKey = Object.keys(NETWORKS).find(key => NETWORKS[key].id === network.id) || 'opal_production';
  return CONTRACT_ADDRESSES[networkKey];
}

// Network status checks
export function getNetworkStatus(networkKey: string): 'active' | 'maintenance' | 'deprecated' {
  switch (networkKey) {
    case 'opal_production':
      return 'active';
    case 'avalanche_fuji':
      return 'deprecated'; // Phase 1 legacy
    case 'local':
      return 'active';
    default:
      return 'deprecated';
  }
}

// Estimated gas costs for operations
export const GAS_ESTIMATES = {
  notarization: 50000,
  commitAudit: 100000,
  registerProject: 160000,
};

// Estimated costs in AVAX (private subnet has very low fees)
export function getEstimatedCost(operation: keyof typeof GAS_ESTIMATES): string {
  const network = getCurrentNetwork();
  const gasLimit = GAS_ESTIMATES[operation];
  
  if (network.id === 43210) { // OPAL Private Subnet
    const costInAvax = (gasLimit * 0.000000025); // 25 gwei base fee
    return `~${costInAvax.toFixed(6)} AVAX`;
  } else {
    const costInAvax = (gasLimit * 0.000000025);
    return `~${costInAvax.toFixed(4)} AVAX`;
  }
}
