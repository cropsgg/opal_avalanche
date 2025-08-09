'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Shield, ExternalLink, Wallet, CheckCircle, Clock } from 'lucide-react';

interface NotarizationProps {
  matterId: string;
  isNotarized: boolean;
  runId: string | null;
}

export function Notarization({ matterId, isNotarized, runId }: NotarizationProps) {
  const [isNotarizing, setIsNotarizing] = useState(false);
  const [walletConnected, setWalletConnected] = useState(false);
  const [txHash, setTxHash] = useState<string | null>(null);

  const handleNotarize = async () => {
    setIsNotarizing(true);
    // Simulate notarization process
    await new Promise(resolve => setTimeout(resolve, 3000));
    setTxHash('0x1234567890abcdef1234567890abcdef12345678');
    setIsNotarizing(false);
  };

  const handleConnectWallet = async () => {
    // Simulate wallet connection
    setWalletConnected(true);
  };

  return (
    <Card className="bg-cream-100 border-stone-200">
      <CardHeader>
        <CardTitle className="text-lg font-display text-brown-900 flex items-center gap-2">
          <Shield className="h-5 w-5" />
          Blockchain Notarization
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {txHash ? (
          // Notarized state
          <div className="text-center py-6">
            <div className="inline-flex p-4 bg-olive-400 text-cream-100 rounded-full mb-4">
              <CheckCircle className="h-8 w-8" />
            </div>
            <h3 className="text-lg font-display font-semibold text-brown-900 mb-2">
              Verified on Avalanche
            </h3>
            <p className="text-brown-500 text-sm mb-4">
              Your legal research run has been cryptographically verified and published on the blockchain.
            </p>
            <div className="bg-white rounded-lg border border-stone-200 p-4 text-left">
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-brown-500">Transaction Hash:</span>
                  <span className="font-mono text-brown-700">{txHash.slice(0, 10)}...{txHash.slice(-8)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-brown-500">Block Number:</span>
                  <span className="text-brown-700">15,432,789</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-brown-500">Timestamp:</span>
                  <span className="text-brown-700">2 hours ago</span>
                </div>
              </div>
            </div>
            <Button variant="outline" className="mt-4 text-brown-700" size="sm">
              <ExternalLink className="h-4 w-4 mr-2" />
              View on Explorer
            </Button>
          </div>
        ) : (
          // Not notarized state
          <div>
            <div className="mb-4">
              <h3 className="text-lg font-display font-semibold text-brown-900 mb-2">
                Secure Your Research
              </h3>
              <p className="text-brown-500 text-sm mb-4">
                Create an immutable, cryptographic proof of your legal research and AI analysis results.
              </p>
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
                    className="w-full bg-brown-700 hover:bg-brown-500 text-cream-100"
                  >
                    Connect Wallet
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="bg-white rounded-lg border border-stone-200 p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-olive-400" />
                      <span className="text-sm font-medium text-brown-900">Wallet Connected</span>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      0x1234...5678
                    </Badge>
                  </div>
                  
                  <div className="text-xs text-brown-500 mb-4">
                    <div className="flex justify-between mb-1">
                      <span>Network:</span>
                      <span>Avalanche Fuji Testnet</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Estimated Cost:</span>
                      <span>~0.001 AVAX</span>
                    </div>
                  </div>
                  
                  <Button 
                    onClick={handleNotarize}
                    disabled={isNotarizing}
                    className="w-full bg-brown-700 hover:bg-brown-500 text-cream-100"
                  >
                    {isNotarizing ? (
                      <>
                        <Clock className="h-4 w-4 mr-2 animate-spin" />
                        Notarizing...
                      </>
                    ) : (
                      <>
                        <Shield className="h-4 w-4 mr-2" />
                        Notarize Research
                      </>
                    )}
                  </Button>
                </div>
                
                <div className="bg-gold-500/10 rounded-lg border border-gold-500 p-4">
                  <h4 className="font-medium text-brown-900 mb-2 text-sm">What gets notarized?</h4>
                  <ul className="text-xs text-brown-700 space-y-1">
                    <li>• Document paragraph hashes</li>
                    <li>• AI agent votes and confidence scores</li>
                    <li>• Citation verification results</li>
                    <li>• Research methodology metadata</li>
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