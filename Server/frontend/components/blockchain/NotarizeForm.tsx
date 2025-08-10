'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { blockchainApi, apiUtils } from '@/lib/api'
import { SubnetNotarizeResponse, EvidenceItem } from '@/types'
import { Loader2, CheckCircle, AlertCircle, Copy, ExternalLink } from 'lucide-react'
import { shortenHash, copyToClipboard } from '@/lib/utils'

export default function NotarizeForm() {
  const [formData, setFormData] = useState({
    runId: '',
    evidenceText: '',
    includeAuditCommit: true,
  })
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<SubnetNotarizeResponse | null>(null)
  const [error, setError] = useState<string>('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')
    setResult(null)

    try {
      // Parse evidence text into items
      const evidenceItems: EvidenceItem[] = formData.evidenceText
        .split('\n\n')
        .filter(text => text.trim())
        .map(text => ({ text: text.trim() }))

      const response = await blockchainApi.notarize({
        run_id: formData.runId,
        documents: [], // Legacy component - no documents
        retrieval_set: evidenceItems,
        include_audit_commit: formData.includeAuditCommit,
      })

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
      // Could add toast notification here
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Subnet Notarization</CardTitle>
          <CardDescription>
            Notarize research evidence on the private Avalanche subnet with Merkle root verification
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="runId" className="block text-sm font-medium mb-2">
                Run ID
              </label>
              <Input
                id="runId"
                type="text"
                placeholder="Enter unique run identifier"
                value={formData.runId}
                onChange={(e) => setFormData({ ...formData, runId: e.target.value })}
                required
              />
            </div>

            <div>
              <label htmlFor="evidenceText" className="block text-sm font-medium mb-2">
                Evidence Text
              </label>
              <Textarea
                id="evidenceText"
                placeholder="Enter legal evidence text (separate multiple items with double line breaks)"
                rows={6}
                value={formData.evidenceText}
                onChange={(e) => setFormData({ ...formData, evidenceText: e.target.value })}
                required
              />
              <p className="text-xs text-muted-foreground mt-1">
                Each paragraph will be hashed separately for Merkle tree construction
              </p>
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="includeAuditCommit"
                checked={formData.includeAuditCommit}
                onChange={(e) => setFormData({ ...formData, includeAuditCommit: e.target.checked })}
                className="rounded border-gray-300"
              />
              <label htmlFor="includeAuditCommit" className="text-sm">
                Include encrypted audit data commit
              </label>
            </div>

            <Button type="submit" disabled={isLoading} className="w-full">
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Notarizing...
                </>
              ) : (
                'Notarize on Subnet'
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
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-green-800">
              <CheckCircle className="h-5 w-5" />
              <span>Notarization Successful</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-green-800 mb-1">
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
                <label className="block text-sm font-medium text-green-800 mb-1">
                  Network
                </label>
                <Badge variant="secondary">{result.network}</Badge>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-green-800 mb-1">
                  Merkle Root
                </label>
                <div className="flex items-center space-x-2">
                  <code className="bg-white px-2 py-1 rounded text-sm border break-all">
                    {result.merkle_root}
                  </code>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCopy(result.merkle_root)}
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-green-800 mb-1">
                  Notary Transaction
                </label>
                <div className="flex items-center space-x-2">
                  <code className="bg-white px-2 py-1 rounded text-sm border">
                    {shortenHash(result.notary_tx_hash)}
                  </code>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCopy(result.notary_tx_hash)}
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-green-800 mb-1">
                  Block Number
                </label>
                <Badge variant="outline">#{result.notary_block_number}</Badge>
              </div>

              {result.commit_tx_hash && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-green-800 mb-1">
                      Audit Commit Transaction
                    </label>
                    <div className="flex items-center space-x-2">
                      <code className="bg-white px-2 py-1 rounded text-sm border">
                        {shortenHash(result.commit_tx_hash)}
                      </code>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleCopy(result.commit_tx_hash!)}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-green-800 mb-1">
                      Commit Block
                    </label>
                    <Badge variant="outline">#{result.commit_block_number}</Badge>
                  </div>
                </>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
