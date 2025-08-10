'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { blockchainApi, apiUtils } from '@/lib/api'
import { BlockchainStatus as BlockchainStatusType } from '@/types'
import { Loader2, RefreshCw, Wifi, WifiOff, Copy, ExternalLink } from 'lucide-react'
import { formatNumber, copyToClipboard } from '@/lib/utils'

export default function BlockchainStatus() {
  const [status, setStatus] = useState<BlockchainStatusType | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const fetchStatus = async () => {
    setIsLoading(true)
    setError('')

    try {
      const response = await blockchainApi.getStatus()
      setStatus(response)
      setLastUpdated(new Date())
    } catch (err) {
      setError(apiUtils.formatError(err))
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchStatus()
  }, [])

  const handleCopy = async (text: string) => {
    try {
      await copyToClipboard(text)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center space-x-2">
              {status?.connected ? (
                <Wifi className="h-5 w-5 text-green-600" />
              ) : (
                <WifiOff className="h-5 w-5 text-red-600" />
              )}
              <span>Blockchain Status</span>
            </CardTitle>
            <CardDescription>
              Private Avalanche subnet connectivity and contract information
            </CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchStatus}
            disabled={isLoading}
          >
            {isLoading ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="mr-2 h-4 w-4" />
            )}
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {status && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Network
                </label>
                <Badge variant="secondary">{status.network}</Badge>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Connection Status
                </label>
                <Badge variant={status.connected ? 'success' : 'destructive'}>
                  {status.connected ? 'Connected' : 'Disconnected'}
                </Badge>
              </div>

              {status.chain_id && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Chain ID
                  </label>
                  <Badge variant="outline">{status.chain_id}</Badge>
                </div>
              )}

              {status.latest_block && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Latest Block
                  </label>
                  <Badge variant="outline">#{formatNumber(status.latest_block)}</Badge>
                </div>
              )}
            </div>

            {Object.keys(status.contract_addresses).length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-3">Contract Addresses</h4>
                <div className="space-y-2">
                  {Object.entries(status.contract_addresses).map(([name, address]) => (
                    <div key={name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <span className="font-medium text-sm capitalize">
                          {name.replace('_', ' ')}
                        </span>
                        <code className="block text-xs text-gray-600 mt-1">
                          {address}
                        </code>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleCopy(address)}
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                        {/* Could add blockchain explorer link here */}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {lastUpdated && (
              <div className="text-xs text-gray-500 border-t pt-4">
                Last updated: {lastUpdated.toLocaleString()}
              </div>
            )}
          </div>
        )}

        {!status && !error && !isLoading && (
          <div className="text-center py-8 text-gray-500">
            <WifiOff className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p>Unable to connect to blockchain</p>
            <Button
              variant="outline"
              size="sm"
              onClick={fetchStatus}
              className="mt-4"
            >
              Try Again
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
