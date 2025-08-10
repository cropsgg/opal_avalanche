'use client';

import { useState, useEffect } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Globe, 
  Lock, 
  Wifi, 
  WifiOff, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Settings 
} from 'lucide-react';
import { getCurrentNetwork, isCorrectNetwork, getNetworkStatus } from '@/lib/config';

interface NetworkStatusProps {
  className?: string;
}

export function NetworkStatus({ className }: NetworkStatusProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [userChainId, setUserChainId] = useState<number | null>(null);
  const [walletAddress, setWalletAddress] = useState<string | null>(null);
  const [networkHealth, setNetworkHealth] = useState<'healthy' | 'degraded' | 'unknown'>('unknown');

  const currentNetwork = getCurrentNetwork();
  const networkStatus = getNetworkStatus(currentNetwork.name);
  const isCorrectNetworkConnected = userChainId ? isCorrectNetwork(userChainId) : false;

  useEffect(() => {
    checkConnection();
    
    // Listen for wallet events
    if (typeof window !== 'undefined' && window.ethereum) {
      const handleAccountsChanged = (accounts: string[]) => {
        setWalletAddress(accounts[0] || null);
        setIsConnected(accounts.length > 0);
      };

      const handleChainChanged = (chainId: string) => {
        setUserChainId(parseInt(chainId, 16));
      };

      window.ethereum.on('accountsChanged', handleAccountsChanged);
      window.ethereum.on('chainChanged', handleChainChanged);

      return () => {
        window.ethereum.removeListener('accountsChanged', handleAccountsChanged);
        window.ethereum.removeListener('chainChanged', handleChainChanged);
      };
    }
  }, []);

  useEffect(() => {
    // Check network health periodically
    const checkHealth = async () => {
      try {
        // Simple health check - try to get block number
        if (typeof window !== 'undefined' && window.ethereum && isConnected) {
          await window.ethereum.request({ method: 'eth_blockNumber' });
          setNetworkHealth('healthy');
        }
      } catch (error) {
        setNetworkHealth('degraded');
      }
    };

    if (isConnected) {
      checkHealth();
      const interval = setInterval(checkHealth, 30000); // Check every 30 seconds
      return () => clearInterval(interval);
    }
  }, [isConnected]);

  const checkConnection = async () => {
    if (typeof window !== 'undefined' && window.ethereum) {
      try {
        const accounts = await window.ethereum.request({ method: 'eth_accounts' });
        const chainId = await window.ethereum.request({ method: 'eth_chainId' });
        
        setIsConnected(accounts.length > 0);
        setWalletAddress(accounts[0] || null);
        setUserChainId(parseInt(chainId, 16));
      } catch (error) {
        setIsConnected(false);
      }
    }
  };

  const getStatusIcon = () => {
    if (!isConnected) {
      return <WifiOff className="h-3 w-3" />;
    }
    
    if (!isCorrectNetworkConnected) {
      return <AlertTriangle className="h-3 w-3" />;
    }
    
    if (networkHealth === 'healthy') {
      return <CheckCircle className="h-3 w-3" />;
    }
    
    if (networkHealth === 'degraded') {
      return <Clock className="h-3 w-3" />;
    }
    
    return <Wifi className="h-3 w-3" />;
  };

  const getStatusColor = () => {
    if (!isConnected) return 'bg-gray-500';
    if (!isCorrectNetworkConnected) return 'bg-red-500';
    if (networkHealth === 'healthy') return 'bg-green-500';
    if (networkHealth === 'degraded') return 'bg-yellow-500';
    return 'bg-blue-500';
  };

  const getStatusText = () => {
    if (!isConnected) return 'Disconnected';
    if (!isCorrectNetworkConnected) return 'Wrong Network';
    if (networkHealth === 'healthy') return 'Connected';
    if (networkHealth === 'degraded') return 'Degraded';
    return 'Connecting';
  };

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="sm" className={`h-8 px-2 ${className}`}>
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <div className="flex items-center gap-1">
              {currentNetwork.isPrivate ? (
                <Lock className="h-3 w-3 text-purple-600" />
              ) : (
                <Globe className="h-3 w-3 text-blue-600" />
              )}
              <span className="text-xs font-medium">{currentNetwork.displayName}</span>
            </div>
            <div className={`w-2 h-2 rounded-full ${getStatusColor()}`} />
          </div>
        </Button>
      </PopoverTrigger>
      
      <PopoverContent className="w-80" align="end">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="font-medium">Network Status</h4>
            <Badge 
              variant="outline" 
              className={`${getStatusColor().replace('bg-', 'border-').replace('500', '200')} text-xs`}
            >
              {getStatusText()}
            </Badge>
          </div>

          {/* Current Network Info */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Network:</span>
              <div className="flex items-center gap-1">
                {currentNetwork.isPrivate ? (
                  <Lock className="h-3 w-3 text-purple-600" />
                ) : (
                  <Globe className="h-3 w-3 text-blue-600" />
                )}
                <span className="font-medium">{currentNetwork.displayName}</span>
              </div>
            </div>
            
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Chain ID:</span>
              <span className="font-mono">{currentNetwork.id}</span>
            </div>
            
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Currency:</span>
              <span>{currentNetwork.nativeCurrency.symbol}</span>
            </div>

            {currentNetwork.requiresVPN && (
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">VPN Required:</span>
                <span className="text-orange-600">Yes</span>
              </div>
            )}
          </div>

          {/* Connection Status */}
          {isConnected && (
            <div className="space-y-2 border-t pt-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Wallet:</span>
                <span className="font-mono text-xs">
                  {walletAddress ? `${walletAddress.slice(0, 6)}...${walletAddress.slice(-4)}` : 'Unknown'}
                </span>
              </div>
              
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Connected Chain:</span>
                <span className={isCorrectNetworkConnected ? 'text-green-600' : 'text-red-600'}>
                  {userChainId || 'Unknown'}
                </span>
              </div>
            </div>
          )}

          {/* Alerts */}
          {currentNetwork.isPrivate && (
            <Alert className="bg-purple-50 border-purple-200">
              <Lock className="h-4 w-4" />
              <AlertDescription className="text-purple-800 text-xs">
                This is a private subnet. Transactions are not publicly visible.
              </AlertDescription>
            </Alert>
          )}

          {networkStatus === 'deprecated' && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription className="text-xs">
                This network is deprecated. Please switch to the OPAL Private Subnet.
              </AlertDescription>
            </Alert>
          )}

          {!isConnected && (
            <Alert>
              <WifiOff className="h-4 w-4" />
              <AlertDescription className="text-xs">
                Connect your wallet to interact with the blockchain.
              </AlertDescription>
            </Alert>
          )}

          {isConnected && !isCorrectNetworkConnected && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription className="text-xs">
                Please switch to {currentNetwork.displayName} in your wallet.
              </AlertDescription>
            </Alert>
          )}

          {currentNetwork.requiresVPN && (
            <Alert className="bg-orange-50 border-orange-200">
              <Settings className="h-4 w-4" />
              <AlertDescription className="text-orange-800 text-xs">
                VPN connection required for private subnet access.
              </AlertDescription>
            </Alert>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}
