'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { blockchainApi, apiUtils } from '@/lib/api'
import { NotarizationStatus } from '@/types'
import { Loader2, Search, CheckCircle, AlertCircle, Copy } from 'lucide-react'
import { shortenHash, copyToClipboard } from '@/lib/utils'

export default function NotarizationLookup() {
  const [runId, setRunId] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<NotarizationStatus | null>(null)
  const [error, setError] = useState<string>('')

  const handleLookup = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!runId.trim()) return

    setIsLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await blockchainApi.getNotarization(runId.trim())
      setResult(response)
    } catch (err) {
      setError(apiUtils.formatError(err))
    } finally {
      setIsLoading(false)
    }
  }

  const handleCopy = async (text: string) => {
    try {
      await copyToClipboard(text)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Notarization Lookup</CardTitle>
          <CardDescription>
            Look up notarization status and verify Merkle root on subnet
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLookup} className="space-y-4">
            <div>
              <label htmlFor="lookupRunId" className="block text-sm font-medium mb-2">
                Run ID
              </label>
              <Input
                id="lookupRunId"
                type="text"
                placeholder="Enter run ID to lookup"
                value={runId}
                onChange={(e) => setRunId(e.target.value)}
                required
              />
            </div>

            <Button type="submit" disabled={isLoading} className="w-full">
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Looking up...
                </>
              ) : (
                <>
                  <Search className="mr-2 h-4 w-4" />
                  Lookup Notarization
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2 text-red-800">
              <AlertCircle className="h-5 w-5" />
              <span className="font-medium">Error</span>
            </div>
            <p className="mt-2 text-sm text-red-700">{error}</p>
          </CardContent>
        </Card>
      )}

      {result && (
        <Card className={`${result.verified ? 'border-green-200 bg-green-50' : 'border-yellow-200 bg-yellow-50'}`}>
          <CardHeader>
            <CardTitle className={`flex items-center space-x-2 ${result.verified ? 'text-green-800' : 'text-yellow-800'}`}>
              {result.verified ? (
                <CheckCircle className="h-5 w-5" />
              ) : (
                <AlertCircle className="h-5 w-5" />
              )}
              <span>
                {result.verified ? 'Notarization Found' : 'Notarization Not Found'}
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className={`block text-sm font-medium mb-1 ${result.verified ? 'text-green-800' : 'text-yellow-800'}`}>
                  Run ID
                </label>
                <div className="flex items-center space-x-2">
                  <code className="bg-white px-2 py-1 rounded text-sm border">
                    {result.run_id}
                  </code>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCopy(result.run_id)}
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <div>
                <label className={`block text-sm font-medium mb-1 ${result.verified ? 'text-green-800' : 'text-yellow-800'}`}>
                  Network
                </label>
                <Badge variant="secondary">{result.network}</Badge>
              </div>

              <div>
                <label className={`block text-sm font-medium mb-1 ${result.verified ? 'text-green-800' : 'text-yellow-800'}`}>
                  Verification Status
                </label>
                <Badge variant={result.verified ? 'success' : 'warning'}>
                  {result.verified ? 'Verified' : 'Not Found'}
                </Badge>
              </div>

              {result.merkle_root && (
                <div className="md:col-span-2">
                  <label className={`block text-sm font-medium mb-1 ${result.verified ? 'text-green-800' : 'text-yellow-800'}`}>
                    Merkle Root
                  </label>
                  <div className="flex items-center space-x-2">
                    <code className="bg-white px-2 py-1 rounded text-sm border break-all">
                      {result.merkle_root}
                    </code>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleCopy(result.merkle_root!)}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              )}

              {result.error && (
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-red-800 mb-1">
                    Error Details
                  </label>
                  <p className="text-sm text-red-700 bg-red-100 p-2 rounded border">
                    {result.error}
                  </p>
                </div>
              )}
            </div>

            {!result.verified && !result.error && (
              <div className="bg-yellow-100 border border-yellow-200 rounded p-4">
                <p className="text-sm text-yellow-800">
                  <strong>Note:</strong> This run ID has not been notarized on the subnet yet, 
                  or the notarization is still pending. Please try again later or verify the run ID.
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
