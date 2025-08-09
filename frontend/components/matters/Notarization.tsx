'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Shield, ExternalLink, Wallet, CheckCircle, Clock, AlertCircle, Loader2, Copy } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import type { NotarizationProof } from '@/types';

interface NotarizationProps {
  matterId: string;
  isNotarized: boolean;
  runId: string | null;
  onNotarized?: () => void;
}

export function Notarization({ matterId, isNotarized, runId, onNotarized }: NotarizationProps) {
  const [isNotarizing, setIsNotarizing] = useState(false);
  const [isCheckingProof, setIsCheckingProof] = useState(false);
  const [walletConnected, setWalletConnected] = useState(false);
  const [walletAddress, setWalletAddress] = useState<string | null>(null);
  const [notarizationProof, setNotarizationProof] = useState<NotarizationProof | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  // Check for existing notarization proof when component mounts
  useEffect(() => {
    if (runId) {
      checkExistingProof();
    }
  }, [runId]);

  // Check if wallet is already connected
  useEffect(() => {
    checkWalletConnection();
  }, []);

  const checkExistingProof = async () => {
    if (!runId) return;
    
    setIsCheckingProof(true);
    try {
      const response = await apiClient.getNotarization(runId);
      if (response.data) {
        setNotarizationProof(response.data);
      }
    } catch (err) {
      console.log('No existing proof found');
    } finally {
      setIsCheckingProof(false);
    }
  };

  const checkWalletConnection = async () => {
    if (typeof window !== 'undefined' && window.ethereum) {
      try {
        const accounts = await window.ethereum.request({ method: 'eth_accounts' });
        if (accounts.length > 0) {
          setWalletConnected(true);
          setWalletAddress(accounts[0]);
        }
      } catch (err) {
        console.log('Wallet not connected');
      }
    }
  };

  const handleConnectWallet = async () => {
    if (typeof window === 'undefined' || !window.ethereum) {
      toast({
        title: 'Wallet Required',
        description: 'Please install MetaMask or another Web3 wallet to continue.',
        variant: 'destructive'
      });
      return;
    }

    try {
      const accounts = await window.ethereum.request({ 
        method: 'eth_requestAccounts' 
      });
      
      if (accounts.length > 0) {
        setWalletConnected(true);
        setWalletAddress(accounts[0]);
        toast({
          title: 'Wallet Connected',
          description: 'Successfully connected to your wallet.',
        });
      }
    } catch (err) {
      console.error('Failed to connect wallet:', err);
      toast({
        title: 'Connection Failed',
        description: 'Failed to connect wallet. Please try again.',
        variant: 'destructive'
      });
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
      const response = await apiClient.notarizeRun(runId);
      
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
          network: 'Avalanche Fuji',
          block_number: response.data.block_number,
          created_at: new Date().toISOString()
        };
        
        setNotarizationProof(proof);
        toast({
          title: 'Notarization Successful',
          description: 'Your research has been verified on the blockchain.',
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
    return `https://testnet.snowtrace.io/tx/${txHash}`;
  };

  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const formatTxHash = (hash: string) => {
    return `${hash.slice(0, 10)}...${hash.slice(-8)}`;
  };

  if (isCheckingProof) {
    return (
      <Card className="bg-cream-100 border-stone-200">
        <CardHeader>
          <CardTitle className="text-lg font-display text-brown-900 flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Blockchain Notarization
          </CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center py-8">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin text-brown-600 mx-auto mb-4" />
            <p className="text-brown-500">Checking for existing proof...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-cream-100 border-stone-200">
      <CardHeader>
        <CardTitle className="text-lg font-display text-brown-900 flex items-center gap-2">
          <Shield className="h-5 w-5" />
          Blockchain Notarization
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {notarizationProof ? (
          // Notarized state
          <div className="text-center py-6">
            <div className="inline-flex p-4 bg-green-500 text-white rounded-full mb-4">
              <CheckCircle className="h-8 w-8" />
            </div>
            <h3 className="text-lg font-display font-semibold text-brown-900 mb-2">
              Verified on Avalanche
            </h3>
            <p className="text-brown-500 text-sm mb-4">
              Your legal research run has been cryptographically verified and published on the blockchain.
            </p>
            
            <div className="bg-white rounded-lg border border-stone-200 p-4 text-left space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-brown-500 text-sm">Transaction Hash:</span>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-brown-700 text-sm">
                    {formatTxHash(notarizationProof.tx_hash)}
                  </span>
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
              
              <div className="flex justify-between items-center">
                <span className="text-brown-500 text-sm">Block Number:</span>
                <span className="text-brown-700 text-sm">{notarizationProof.block_number}</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-brown-500 text-sm">Network:</span>
                <Badge variant="outline" className="text-xs">{notarizationProof.network}</Badge>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-brown-500 text-sm">Merkle Root:</span>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-brown-700 text-sm">
                    {formatTxHash(notarizationProof.merkle_root)}
                  </span>
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
            
            <div className="flex gap-2 mt-4">
              <Button 
                variant="outline" 
                className="text-brown-700 flex-1" 
                size="sm"
                onClick={() => window.open(getExplorerUrl(notarizationProof.tx_hash), '_blank')}
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                View on Explorer
              </Button>
              <Button 
                variant="outline" 
                className="text-brown-700" 
                size="sm"
                onClick={() => copyToClipboard(JSON.stringify(notarizationProof, null, 2))}
              >
                <Copy className="h-4 w-4 mr-2" />
                Copy Proof
              </Button>
            </div>
          </div>
        ) : (
          // Not notarized state
          <div>
            <div className="mb-4">
              <h3 className="text-lg font-display font-semibold text-brown-900 mb-2">
                Secure Your Research
              </h3>
              <p className="text-brown-500 text-sm mb-4">
                Create an immutable, cryptographic proof of your legal research and AI analysis results on the Avalanche blockchain.
              </p>
              
              {!runId && (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    Make a research query first to enable notarization.
                  </AlertDescription>
                </Alert>
              )}
            </div>

            {!walletConnected ? (
              <div className="space-y-3">
                <div className="bg-white rounded-lg border border-stone-200 p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <Wallet className="h-5 w-5 text-brown-500" />
                    <div>
                      <h4 className="font-medium text-brown-900">Connect Wallet</h4>
                      <p className="text-sm text-brown-500">Required for blockchain notarization</p>
                    </div>
                  </div>
                  <Button 
                    onClick={handleConnectWallet}
                    className="w-full bg-brown-700 hover:bg-brown-600 text-cream-100"
                  >
                    <Wallet className="h-4 w-4 mr-2" />
                    Connect Wallet
                  </Button>
                </div>
                
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    Need a Web3 wallet like MetaMask? Install it from{' '}
                    <a href="https://metamask.io" target="_blank" rel="noopener noreferrer" className="underline">
                      metamask.io
                    </a>
                  </AlertDescription>
                </Alert>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="bg-white rounded-lg border border-stone-200 p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span className="text-sm font-medium text-brown-900">Wallet Connected</span>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {walletAddress ? formatAddress(walletAddress) : 'Connected'}
                    </Badge>
                  </div>
                  
                  <div className="text-xs text-brown-500 mb-4 space-y-1">
                    <div className="flex justify-between">
                      <span>Network:</span>
                      <span>Avalanche Fuji Testnet</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Estimated Cost:</span>
                      <span>~0.001 AVAX</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Status:</span>
                      <span className={runId ? 'text-green-600' : 'text-orange-600'}>
                        {runId ? 'Ready to notarize' : 'No research run available'}
                      </span>
                    </div>
                  </div>
                  
                  <Button 
                    onClick={handleNotarize}
                    disabled={isNotarizing || !runId}
                    className="w-full bg-brown-700 hover:bg-brown-600 text-cream-100 disabled:opacity-50"
                  >
                    {isNotarizing ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Notarizing on Avalanche...
                      </>
                    ) : (
                      <>
                        <Shield className="h-4 w-4 mr-2" />
                        Notarize Research
                      </>
                    )}
                  </Button>
                </div>
                
                <div className="bg-blue-50 rounded-lg border border-blue-200 p-4">
                  <h4 className="font-medium text-blue-900 mb-2 text-sm flex items-center gap-2">
                    <Shield className="h-4 w-4" />
                    What gets notarized?
                  </h4>
                  <ul className="text-xs text-blue-800 space-y-1">
                    <li>• Cryptographic hashes of all cited paragraphs</li>
                    <li>• AI agent voting results and confidence scores</li>
                    <li>• Legal authority verification metadata</li>
                    <li>• Research run timestamp and methodology</li>
                    <li>• Merkle tree proof for document integrity</li>
                  </ul>
                </div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Extend the Window interface for TypeScript
declare global {
  interface Window {
    ethereum?: any;
  }
}