'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Shield, 
  ExternalLink, 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  Loader2, 
  Copy,
  Lock,
  Globe,
  Eye,
  EyeOff,
  Info,
  Server
} from 'lucide-react';
import { apiClient } from '@/lib/api';
import { getCurrentNetwork, getEstimatedCost } from '@/lib/config';
import { useToast } from '@/hooks/use-toast';
import type { NotarizationProof } from '@/types';

interface SubnetNotarizationProps {
  matterId: string;
  isNotarized: boolean;
  runId: string | null;
  onNotarized?: () => void;
}

export function SubnetNotarization({ matterId, isNotarized, runId, onNotarized }: SubnetNotarizationProps) {
  const [isNotarizing, setIsNotarizing] = useState(false);
  const [isCheckingProof, setIsCheckingProof] = useState(false);
  const [notarizationProof, setNotarizationProof] = useState<NotarizationProof | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [usePrivateSubnet, setUsePrivateSubnet] = useState(true);
  const [showNetworkDetails, setShowNetworkDetails] = useState(false);
  const { toast } = useToast();

  const currentNetwork = getCurrentNetwork();

  // Check for existing notarization proof when component mounts
  useEffect(() => {
    if (runId) {
      checkExistingProof();
    }
  }, [runId, usePrivateSubnet]);

  const checkExistingProof = async () => {
    if (!runId) return;
    
    setIsCheckingProof(true);
    try {
      const response = await apiClient.getNotarization(runId, usePrivateSubnet);
      if (response.data) {
        setNotarizationProof(response.data);
      }
    } catch (err) {
      console.log('No existing proof found');
    } finally {
      setIsCheckingProof(false);
    }
  };

  const handleNotarize = async () => {
    if (!runId) {
      toast({
        title: 'No Run Selected',
        description: 'Please make a research query first to notarize.',
        variant: 'destructive'
      });
      return;
    }

    setIsNotarizing(true);
    setError(null);

    try {
      const response = await apiClient.notarizeRun(runId, usePrivateSubnet);
      
      if (response.error) {
        setError(response.error);
        toast({
          title: 'Notarization Failed',
          description: response.error,
          variant: 'destructive'
        });
        return;
      }

      if (response.data) {
        const proof: NotarizationProof = {
          run_id: runId,
          merkle_root: response.data.merkle_root,
          tx_hash: response.data.tx_hash,
          network: response.data.network || currentNetwork.displayName,
          network_id: response.data.network_id || currentNetwork.id,
          block_number: response.data.block_number,
          contract_address: response.data.contract_address,
          gas_used: response.data.gas_used,
          confirmation_count: response.data.confirmation_count,
          created_at: new Date().toISOString(),
          is_private_subnet: response.data.is_private_subnet || usePrivateSubnet
        };
        
        setNotarizationProof(proof);
        toast({
          title: 'Notarization Successful',
          description: `Research verified on ${proof.is_private_subnet ? 'private' : 'public'} blockchain.`,
        });

        // Notify parent component
        if (onNotarized) {
          onNotarized();
        }
      }
    } catch (err) {
      console.error('Notarization error:', err);
      const errorMsg = err instanceof Error ? err.message : 'Failed to notarize';
      setError(errorMsg);
      toast({
        title: 'Notarization Failed',
        description: 'An unexpected error occurred. Please try again.',
        variant: 'destructive'
      });
    } finally {
      setIsNotarizing(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: 'Copied',
      description: 'Copied to clipboard',
    });
  };

  const getExplorerUrl = (txHash: string) => {
    return currentNetwork.explorerUrl ? `${currentNetwork.explorerUrl}/tx/${txHash}` : null;
  };

  const formatAddress = (address: string) =>
    `${address.slice(0, 6)}...${address.slice(-4)}`;

  // Show loading state while checking for existing proof
  if (isCheckingProof) {
    return (
      <Card className="border-stone-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-brown-900">
            <Shield className="h-5 w-5" />
            Blockchain Verification
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-brown-600" />
            <span className="ml-2 text-brown-600">Checking for existing proof...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Show proof if already notarized
  if (notarizationProof) {
    const explorerUrl = getExplorerUrl(notarizationProof.tx_hash);
    
    return (
      <Card className="border-green-200 bg-green-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-green-800">
            <Shield className="h-5 w-5" />
            Blockchain Verified
            {notarizationProof.is_private_subnet && (
              <Badge variant="outline" className="text-xs bg-purple-100 text-purple-800 border-purple-300">
                <Lock className="h-3 w-3 mr-1" />
                Private
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert className="bg-green-100 border-green-300">
            <CheckCircle className="h-4 w-4" />
            <AlertDescription className="text-green-800">
              This research has been cryptographically verified and recorded on the blockchain.
              {notarizationProof.is_private_subnet && " The verification is stored on OPAL's private subnet for enhanced privacy."}
              {!notarizationProof.is_private_subnet && " All transactions are paid by OPAL servers - no cost to you."}
            </AlertDescription>
          </Alert>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <div>
                <label className="text-xs font-medium text-green-700">Network</label>
                <div className="flex items-center gap-2">
                  <p className="text-sm text-green-800">{notarizationProof.network}</p>
                  {notarizationProof.is_private_subnet ? (
                    <Lock className="h-3 w-3 text-purple-600" />
                  ) : (
                    <Globe className="h-3 w-3 text-blue-600" />
                  )}
                </div>
              </div>
              
              <div>
                <label className="text-xs font-medium text-green-700">Transaction Hash</label>
                <div className="flex items-center gap-2">
                  <p className="text-xs font-mono text-green-800">
                    {formatAddress(notarizationProof.tx_hash)}
                  </p>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(notarizationProof.tx_hash)}
                    className="h-6 w-6 p-0"
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                </div>
              </div>

              <div>
                <label className="text-xs font-medium text-green-700">Merkle Root</label>
                <div className="flex items-center gap-2">
                  <p className="text-xs font-mono text-green-800">
                    {formatAddress(notarizationProof.merkle_root)}
                  </p>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(notarizationProof.merkle_root)}
                    className="h-6 w-6 p-0"
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-xs font-medium text-green-700">Block Number</label>
                <p className="text-sm text-green-800">#{notarizationProof.block_number.toLocaleString()}</p>
              </div>

              {notarizationProof.gas_used && (
                <div>
                  <label className="text-xs font-medium text-green-700">Gas Used</label>
                  <p className="text-sm text-green-800">{notarizationProof.gas_used.toLocaleString()}</p>
                </div>
              )}

              <div>
                <label className="text-xs font-medium text-green-700">Verified At</label>
                <p className="text-sm text-green-800">
                  {new Date(notarizationProof.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>

          {explorerUrl && !notarizationProof.is_private_subnet && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => window.open(explorerUrl, '_blank')}
              className="w-full"
            >
              <ExternalLink className="h-4 w-4 mr-2" />
              View on Explorer
            </Button>
          )}

          {notarizationProof.is_private_subnet && (
            <Alert className="bg-purple-50 border-purple-200">
              <Info className="h-4 w-4" />
              <AlertDescription className="text-purple-800">
                This verification is stored on OPAL's private subnet. Only authorized parties can access the transaction details.
                <strong> No charges apply to your account</strong> - all blockchain costs are covered by OPAL.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-stone-200">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-brown-900">
          <Shield className="h-5 w-5" />
          Blockchain Verification
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Tabs value={usePrivateSubnet ? "private" : "public"} onValueChange={(value) => setUsePrivateSubnet(value === "private")}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="private" className="flex items-center gap-2">
              <Lock className="h-4 w-4" />
              Private Subnet
            </TabsTrigger>
            <TabsTrigger value="public" className="flex items-center gap-2">
              <Globe className="h-4 w-4" />
              Public Network
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="private" className="space-y-4">
            <Alert className="bg-purple-50 border-purple-200">
              <Lock className="h-4 w-4" />
              <AlertDescription className="text-purple-800">
                <strong>OPAL Private Subnet</strong> - Enhanced privacy with server-paid transactions. No wallet connection required.
              </AlertDescription>
            </Alert>
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-brown-600">Network:</span>
                <span className="ml-2 font-medium">{currentNetwork.displayName}</span>
              </div>
              <div>
                <span className="text-brown-600">Privacy:</span>
                <span className="ml-2 font-medium text-purple-600">Maximum</span>
              </div>
              <div>
                <span className="text-brown-600">Cost to You:</span>
                <span className="ml-2 font-medium text-green-600">Free</span>
              </div>
              <div>
                <span className="text-brown-600">Paid By:</span>
                <span className="ml-2 font-medium">OPAL Server</span>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="public" className="space-y-4">
            <Alert className="bg-blue-50 border-blue-200">
              <Globe className="h-4 w-4" />
              <AlertDescription className="text-blue-800">
                <strong>Public Network</strong> - Legacy support for Avalanche Fuji testnet. Server-paid transactions.
              </AlertDescription>
            </Alert>
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-brown-600">Network:</span>
                <span className="ml-2 font-medium">Avalanche Fuji</span>
              </div>
              <div>
                <span className="text-brown-600">Privacy:</span>
                <span className="ml-2 font-medium text-blue-600">Public</span>
              </div>
              <div>
                <span className="text-brown-600">Cost to You:</span>
                <span className="ml-2 font-medium text-green-600">Free</span>
              </div>
              <div>
                <span className="text-brown-600">Status:</span>
                <span className="ml-2 font-medium text-orange-600">Legacy</span>
              </div>
            </div>
          </TabsContent>
        </Tabs>

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Server-Based Notarization */}
        <div className="space-y-3">
          <div className="bg-white rounded-lg border border-stone-200 p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Server className="h-4 w-4 text-green-500" />
                <span className="text-sm font-medium text-brown-900">Server-Paid Verification</span>
              </div>
              <Badge variant="outline" className="text-xs bg-green-50 text-green-700 border-green-300">
                No Wallet Required
              </Badge>
            </div>

            <div className="text-xs text-brown-500 space-y-1">
              <div className="flex justify-between">
                <span>Network:</span>
                <span className="text-brown-700">
                  {usePrivateSubnet ? currentNetwork.displayName : 'Avalanche Fuji'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Transaction Cost:</span>
                <span className="text-green-600 font-medium">Paid by OPAL</span>
              </div>
              <div className="flex justify-between">
                <span>Your Cost:</span>
                <span className="text-green-600 font-medium">$0.00</span>
              </div>
              <div className="flex justify-between">
                <span>Status:</span>
                <span className={runId ? 'text-green-600' : 'text-orange-600'}>
                  {runId ? 'Ready to verify' : 'Complete research first'}
                </span>
              </div>
            </div>
          </div>

          {/* Notarize Button */}
          <Button 
            onClick={handleNotarize}
            disabled={isNotarizing || !runId}
            className="w-full bg-brown-700 hover:bg-brown-600"
          >
            {isNotarizing ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Verifying on {usePrivateSubnet ? 'Private Subnet' : 'Public Network'}...
              </>
            ) : (
              <>
                <Shield className="h-4 w-4 mr-2" />
                Verify on Blockchain (Server Paid)
              </>
            )}
          </Button>

          {/* Information Alert */}
          <Alert className="bg-blue-50 border-blue-200">
            <Info className="h-4 w-4" />
            <AlertDescription className="text-blue-800">
              <strong>No wallet connection needed.</strong> OPAL's servers handle all blockchain transactions and pay all associated costs. 
              Your research will be cryptographically verified and stored {usePrivateSubnet ? 'privately' : 'publicly'} on the blockchain.
            </AlertDescription>
          </Alert>

          {/* Network Details Toggle */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowNetworkDetails(!showNetworkDetails)}
            className="w-full text-xs"
          >
            {showNetworkDetails ? <EyeOff className="h-3 w-3 mr-1" /> : <Eye className="h-3 w-3 mr-1" />}
            {showNetworkDetails ? 'Hide' : 'Show'} Technical Details
          </Button>

          {showNetworkDetails && (
            <div className="bg-stone-50 rounded-lg p-3 text-xs space-y-2">
              <div className="flex justify-between">
                <span>Chain ID:</span>
                <span className="font-mono">{currentNetwork.id}</span>
              </div>
              <div className="flex justify-between">
                <span>RPC Endpoint:</span>
                <span className="font-mono truncate max-w-32" title={currentNetwork.rpcUrl}>
                  {usePrivateSubnet ? 'Private (VPN Only)' : currentNetwork.rpcUrl}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Gas Token:</span>
                <span>{currentNetwork.nativeCurrency.symbol}</span>
              </div>
              <div className="flex justify-between">
                <span>Privacy Level:</span>
                <span className={usePrivateSubnet ? 'text-purple-600' : 'text-blue-600'}>
                  {usePrivateSubnet ? 'Private Subnet' : 'Public Testnet'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Payment Method:</span>
                <span className="text-green-600">Server Account</span>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
