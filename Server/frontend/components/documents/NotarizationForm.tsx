'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Separator } from '@/components/ui/separator'
import { Loader2, Shield, Upload, AlertCircle, CheckCircle2 } from 'lucide-react'
import { Document, SubnetNotarizeRequest, SubnetNotarizeResponse } from '@/types'
import { blockchainApi, apiUtils } from '@/lib/api'

interface NotarizationFormProps {
  documents: Document[]
  onNotarizationComplete?: (result: SubnetNotarizeResponse) => void
}

export default function NotarizationForm({ 
  documents, 
  onNotarizationComplete 
}: NotarizationFormProps) {
  const [runId, setRunId] = useState(`run_${Date.now()}`)
  const [includeAudit, setIncludeAudit] = useState(true)
  const [additionalEvidence, setAdditionalEvidence] = useState('')
  const [metadata, setMetadata] = useState('')
  const [isNotarizing, setIsNotarizing] = useState(false)
  const [result, setResult] = useState<SubnetNotarizeResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleNotarize = async () => {
    if (documents.length === 0) {
      setError('Please add at least one document to notarize')
      return
    }

    setIsNotarizing(true)
    setError(null)
    setResult(null)

    try {
      // Parse additional evidence
      const retrievalSet = additionalEvidence.trim() 
        ? additionalEvidence.split('\n').filter(line => line.trim()).map(line => ({
            text: line.trim(),
            source: 'manual_entry'
          }))
        : []

      // Parse metadata
      let parsedMetadata = {}
      if (metadata.trim()) {
        try {
          parsedMetadata = JSON.parse(metadata)
        } catch {
          // If not valid JSON, treat as key-value string
          parsedMetadata = { note: metadata.trim() }
        }
      }

      const request: SubnetNotarizeRequest = {
        run_id: runId,
        documents,
        retrieval_set: retrievalSet,
        include_audit_commit: includeAudit,
        metadata: parsedMetadata
      }

      const response = await blockchainApi.notarize(request)
      setResult(response)
      onNotarizationComplete?.(response)

    } catch (err: any) {
      setError(apiUtils.formatError(err))
    } finally {
      setIsNotarizing(false)
    }
  }

  const generateNewRunId = () => {
    setRunId(`run_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`)
  }

  const getTotalContent = () => {
    const docChars = documents.reduce((total, doc) => total + doc.content.length, 0)
    const evidenceChars = additionalEvidence.length
    return docChars + evidenceChars
  }

  if (result) {
    return (
      <Card className="border-green-200 bg-green-50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-green-800">
            <CheckCircle2 className="h-5 w-5" />
            <span>Notarization Complete</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-green-700">Run ID</label>
              <div className="mt-1 p-2 bg-white border rounded font-mono text-sm">
                {result.run_id}
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-green-700">Network</label>
              <div className="mt-1 p-2 bg-white border rounded">
                <Badge variant="outline">{result.network}</Badge>
              </div>
            </div>
          </div>

          <div>
            <label className="text-sm font-medium text-green-700">Merkle Root</label>
            <div className="mt-1 p-2 bg-white border rounded font-mono text-sm break-all">
              {result.merkle_root}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-green-700">Notary Transaction</label>
              <div className="mt-1 p-2 bg-white border rounded font-mono text-xs break-all">
                {result.notary_tx_hash}
              </div>
              <div className="text-xs text-green-600 mt-1">
                Block: {result.notary_block_number}
              </div>
            </div>
            {result.commit_tx_hash && (
              <div>
                <label className="text-sm font-medium text-green-700">Audit Commit</label>
                <div className="mt-1 p-2 bg-white border rounded font-mono text-xs break-all">
                  {result.commit_tx_hash}
                </div>
                <div className="text-xs text-green-600 mt-1">
                  Block: {result.commit_block_number}
                </div>
              </div>
            )}
          </div>

          <div className="bg-white p-4 rounded border">
            <h4 className="font-medium text-green-800 mb-2">Gas Usage & Cost</h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              {Object.entries(result.gas_used).map(([operation, gas]) => (
                <div key={operation}>
                  <span className="font-medium capitalize">{operation}:</span>
                  <span className="ml-1">{gas.toLocaleString()} gas</span>
                </div>
              ))}
              <div className="col-span-2 pt-2 border-t">
                <span className="font-medium">Total Cost:</span>
                <span className="ml-1 text-green-700">{result.total_cost}</span>
              </div>
            </div>
          </div>

          <Button 
            onClick={() => {
              setResult(null)
              setError(null)
              generateNewRunId()
            }}
            className="w-full"
          >
            Notarize Another Set
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Shield className="h-5 w-5" />
          <span>Notarize Documents</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 text-red-800">
              <AlertCircle className="h-5 w-5" />
              <span className="font-medium">Notarization Failed</span>
            </div>
            <p className="text-red-700 mt-1">{error}</p>
          </div>
        )}

        {/* Run Configuration */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">Run ID</label>
            <Button 
              onClick={generateNewRunId}
              variant="outline" 
              size="sm"
            >
              Generate New
            </Button>
          </div>
          <Input
            value={runId}
            onChange={(e) => setRunId(e.target.value)}
            placeholder="Unique identifier for this notarization"
          />
        </div>

        {/* Documents Summary */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-medium mb-2">Documents to Notarize</h4>
          {documents.length === 0 ? (
            <div className="text-gray-500 text-center py-4">
              No documents added yet
            </div>
          ) : (
            <div className="space-y-2">
              {documents.map((doc, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <span className="font-medium">{doc.title}</span>
                  <Badge variant="outline">
                    {doc.content.length.toLocaleString()} chars
                  </Badge>
                </div>
              ))}
              <Separator />
              <div className="flex items-center justify-between font-medium">
                <span>Total: {documents.length} documents</span>
                <span>{getTotalContent().toLocaleString()} characters</span>
              </div>
            </div>
          )}
        </div>

        {/* Additional Evidence */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Additional Evidence (Optional)</label>
          <Textarea
            value={additionalEvidence}
            onChange={(e) => setAdditionalEvidence(e.target.value)}
            placeholder="Enter additional evidence or supporting text (one piece per line)"
            rows={4}
            className="resize-y"
          />
          <p className="text-xs text-gray-500">
            Each line will be treated as separate evidence
          </p>
        </div>

        {/* Metadata */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Metadata (Optional)</label>
          <Textarea
            value={metadata}
            onChange={(e) => setMetadata(e.target.value)}
            placeholder='{"case_id": "CASE-2024-001", "client": "Example Corp"}'
            rows={3}
            className="resize-y font-mono text-sm"
          />
          <p className="text-xs text-gray-500">
            JSON format or free text for additional context
          </p>
        </div>

        {/* Options */}
        <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
          <div>
            <div className="font-medium text-blue-900">Include Encrypted Audit Trail</div>
            <div className="text-sm text-blue-700">
              Store encrypted copy of all documents and metadata on subnet
            </div>
          </div>
          <Switch
            checked={includeAudit}
            onCheckedChange={setIncludeAudit}
          />
        </div>

        {/* Submit */}
        <Button
          onClick={handleNotarize}
          disabled={isNotarizing || documents.length === 0}
          className="w-full"
          size="lg"
        >
          {isNotarizing ? (
            <>
              <Loader2 className="h-5 w-5 mr-2 animate-spin" />
              Notarizing on Subnet...
            </>
          ) : (
            <>
              <Upload className="h-5 w-5 mr-2" />
              Notarize {documents.length} Document{documents.length !== 1 ? 's' : ''}
            </>
          )}
        </Button>

        {/* Gas Fee Notice */}
        <div className="text-center text-sm text-gray-600 bg-gray-50 p-3 rounded">
          <strong>Note:</strong> All blockchain gas fees are paid by the server. 
          You will not be charged for notarization costs.
        </div>
      </CardContent>
    </Card>
  )
}
