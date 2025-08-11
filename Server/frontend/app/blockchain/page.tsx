'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import BlockchainStatus from '@/components/blockchain/BlockchainStatus'
import NotarizationLookup from '@/components/blockchain/NotarizationLookup'
import DocumentUploader from '@/components/documents/DocumentUploader'
import DocumentHashResults from '@/components/documents/DocumentHashResults'
import NotarizationForm from '@/components/documents/NotarizationForm'
import { Blocks, FileText, Hash, Shield, Search, Zap, Sparkles, Lock, CheckCircle, AlertCircle, ArrowRight, RotateCcw, Activity } from 'lucide-react'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { Document, DocumentHashResponse, SubnetNotarizeResponse, BlockchainStatus as BlockchainStatusType } from '@/types'
import { blockchainApi, healthApi } from '@/lib/api'

export default function BlockchainPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedTransaction, setSelectedTransaction] = useState<string>()
  const [activeView, setActiveView] = useState('operations')
  const [blockchainStatus, setBlockchainStatus] = useState<BlockchainStatusType | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [documents, setDocuments] = useState<Document[]>([])
  const [isHashing, setIsHashing] = useState(false)

  useEffect(() => {
    loadBlockchainStatus()
  }, [])

  const loadBlockchainStatus = async () => {
    try {
      setIsLoading(true)
      const status = await blockchainApi.getStatus()
      setBlockchainStatus(status)
    } catch (error) {
      console.error('Failed to load blockchain status:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleHashDocuments = async () => {
    if (documents.length === 0) return
    
    setIsHashing(true)
    try {
      const response = await blockchainApi.hashDocuments({ documents })
      console.log('Documents hashed:', response)
    } catch (error) {
      console.error('Failed to hash documents:', error)
    } finally {
      setIsHashing(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 flex items-center justify-center">
        <div className="text-center space-y-4">
          <LoadingSpinner size="lg" />
          <p className="text-gray-600 font-medium">Loading blockchain status...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      {/* Hero Header */}
      <section className="relative py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex items-center justify-center mb-6">
            <div className="relative">
              <div className="flex items-center justify-center w-20 h-20 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-lg">
                <Blocks className="h-10 w-10 text-white" />
              </div>
              <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                {blockchainStatus?.connected ? (
                <CheckCircle className="w-4 h-4 text-white" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-white" />
                )}
              </div>
            </div>
          </div>
          
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 tracking-tight mb-6">
            Blockchain Operations
            <span className="block text-2xl md:text-3xl text-blue-600 font-normal mt-2">
              Document Notarization & Audit System
            </span>
          </h1>

          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
            Secure document notarization on Avalanche subnet with cryptographic integrity proofs and encrypted audit trails.
          </p>

          <div className="flex flex-wrap justify-center gap-4 mb-8">
            <div className="bg-white/80 backdrop-blur-sm px-4 py-2 rounded-lg border border-blue-200 flex items-center space-x-2">
              <Activity className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-700">
                Network: {blockchainStatus?.connected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            {blockchainStatus?.chain_id && (
            <div className="bg-white/80 backdrop-blur-sm px-4 py-2 rounded-lg border border-green-200 flex items-center space-x-2">
              <Shield className="h-4 w-4 text-green-600" />
                <span className="text-sm font-medium text-green-700">Chain ID: {blockchainStatus.chain_id}</span>
            </div>
            )}
            {blockchainStatus?.latest_block && (
            <div className="bg-white/80 backdrop-blur-sm px-4 py-2 rounded-lg border border-purple-200 flex items-center space-x-2">
              <Sparkles className="h-4 w-4 text-purple-600" />
                <span className="text-sm font-medium text-purple-700">Block: #{blockchainStatus.latest_block}</span>
            </div>
            )}
          </div>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
        <Tabs value={activeView} onValueChange={setActiveView} className="space-y-8">
          <TabsList className="grid w-full grid-cols-3 bg-white/60 backdrop-blur-sm p-2 rounded-2xl">
            <TabsTrigger value="operations" className="flex items-center space-x-2">
              <FileText className="h-4 w-4" />
              <span>Document Operations</span>
            </TabsTrigger>
            <TabsTrigger value="status" className="flex items-center space-x-2">
              <Activity className="h-4 w-4" />
              <span>Network Status</span>
            </TabsTrigger>
            <TabsTrigger value="lookup" className="flex items-center space-x-2">
              <Search className="h-4 w-4" />
              <span>Verification Lookup</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="operations" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Document Upload */}
              <Card className="bg-white/80 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <FileText className="h-5 w-5" />
                    <span>Document Upload</span>
                  </CardTitle>
                  <CardDescription>
                    Upload documents for hashing and notarization
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <DocumentUploader 
                    documents={documents}
                    onDocumentsChange={setDocuments}
                    onHashDocuments={handleHashDocuments}
                    isHashing={isHashing}
                  />
                </CardContent>
              </Card>

              {/* Notarization Form */}
              <Card className="bg-white/80 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Lock className="h-5 w-5" />
                    <span>Notarization</span>
                  </CardTitle>
                  <CardDescription>
                    Submit documents for blockchain notarization
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <NotarizationForm 
                    documents={documents}
                    onNotarizationComplete={(result) => {
                      console.log('Notarization completed:', result)
                    }}
                  />
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="status" className="space-y-6">
            <BlockchainStatus />
          </TabsContent>

          <TabsContent value="lookup" className="space-y-6">
            <NotarizationLookup />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}