'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Hash, Copy, FileText, Zap, DollarSign } from 'lucide-react'
import { DocumentHashResponse } from '@/types'
import { copyToClipboard } from '@/lib/utils'

interface DocumentHashResultsProps {
  results: DocumentHashResponse
}

export default function DocumentHashResults({ results }: DocumentHashResultsProps) {
  const handleCopy = async (text: string, label: string) => {
    try {
      await copyToClipboard(text)
      // Could add toast notification here
    } catch (error) {
      console.error(`Failed to copy ${label}:`, error)
    }
  }

  return (
    <div className="space-y-6">
      {/* Merkle Root */}
      <Card className="border-green-200 bg-green-50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-green-800">
            <Hash className="h-5 w-5" />
            <span>Merkle Root</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2">
            <code className="flex-1 p-3 bg-white border rounded font-mono text-sm break-all">
              {results.merkle_root}
            </code>
            <Button
              onClick={() => handleCopy(results.merkle_root, 'Merkle root')}
              variant="outline"
              size="sm"
            >
              <Copy className="h-4 w-4" />
            </Button>
          </div>
          <p className="text-sm text-green-700 mt-2">
            This is the cryptographic proof of your documents&apos; integrity
          </p>
        </CardContent>
      </Card>

      {/* Gas Estimates */}
      <Card className="border-blue-200 bg-blue-50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-blue-800">
            <DollarSign className="h-5 w-5" />
            <span>Gas Cost Estimates</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Notary Cost */}
            <div className="text-center p-4 bg-white rounded-lg border">
              <div className="text-2xl font-bold text-blue-600">
                {results.gas_estimate.notary.cost_avax}
              </div>
              <div className="text-sm text-gray-600">Notary Cost</div>
              <div className="text-xs text-gray-500 mt-1">
                {results.gas_estimate.notary.gas_limit.toLocaleString()} gas
              </div>
            </div>

            {/* Commit Cost */}
            <div className="text-center p-4 bg-white rounded-lg border">
              <div className="text-2xl font-bold text-blue-600">
                {results.gas_estimate.commit.cost_avax}
              </div>
              <div className="text-sm text-gray-600">Audit Commit</div>
              <div className="text-xs text-gray-500 mt-1">
                {results.gas_estimate.commit.gas_limit.toLocaleString()} gas
              </div>
            </div>

            {/* Total Cost */}
            <div className="text-center p-4 bg-blue-100 rounded-lg border border-blue-300">
              <div className="text-2xl font-bold text-blue-800">
                {results.gas_estimate.total.cost_avax}
              </div>
              <div className="text-sm text-blue-700 font-medium">Total Cost</div>
              <div className="text-xs text-blue-600 mt-1">
                {results.gas_estimate.total.gas_limit.toLocaleString()} gas
              </div>
            </div>
          </div>

          <div className="text-sm text-blue-700 bg-blue-100 p-3 rounded">
            <strong>Note:</strong> {results.gas_estimate.note}
          </div>
        </CardContent>
      </Card>

      {/* Document Details */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileText className="h-5 w-5" />
            <span>Document Hashes</span>
            <Badge variant="outline">{results.total_documents} documents</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {results.documents.map((doc, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium">{doc.title}</h4>
                  <Badge variant="outline">
                    {doc.content_length.toLocaleString()} chars
                  </Badge>
                </div>
                
                <div className="text-sm text-gray-600 mb-2">
                  {doc.content_preview}
                </div>
                
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-500">Hash:</span>
                  <code className="flex-1 text-xs font-mono bg-gray-100 p-1 rounded break-all">
                    {doc.hash}
                  </code>
                  <Button
                    onClick={() => handleCopy(doc.hash, `${doc.title} hash`)}
                    variant="outline"
                    size="sm"
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Technical Details */}
      <Card className="border-gray-200 bg-gray-50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-gray-700">
            <Zap className="h-5 w-5" />
            <span>Technical Details</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-gray-600">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="font-medium">Hashing Algorithm:</span>
              <div>Keccak-256 (Ethereum standard)</div>
            </div>
            <div>
              <span className="font-medium">Merkle Tree:</span>
              <div>Binary tree with duplicate handling</div>
            </div>
            <div>
              <span className="font-medium">Gas Price:</span>
              <div>{results.gas_estimate.notary.gas_price_gwei} Gwei</div>
            </div>
            <div>
              <span className="font-medium">Audit Data Size:</span>
              <div>{results.gas_estimate.commit.estimated_data_size_kb} KB (estimated)</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
