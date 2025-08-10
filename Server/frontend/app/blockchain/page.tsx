'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import BlockchainStatus from '@/components/blockchain/BlockchainStatus'
import NotarizationLookup from '@/components/blockchain/NotarizationLookup'
import DocumentUploader from '@/components/documents/DocumentUploader'
import DocumentHashResults from '@/components/documents/DocumentHashResults'
import NotarizationForm from '@/components/documents/NotarizationForm'
import { Blocks, FileText, Hash, Shield, Search, Zap, Sparkles, Lock, CheckCircle, AlertCircle, ArrowRight, RotateCcw } from 'lucide-react'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { Document, DocumentHashResponse, SubnetNotarizeResponse } from '@/types'
import { blockchainApi, apiUtils } from '@/lib/api'

export default function BlockchainPage() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [hashResults, setHashResults] = useState<DocumentHashResponse | null>(null)
  const [isHashing, setIsHashing] = useState(false)
  const [notarizationResult, setNotarizationResult] = useState<SubnetNotarizeResponse | null>(null)
  const [activeTab, setActiveTab] = useState('documents')

  const handleHashDocuments = async () => {
    if (documents.length === 0) return

    setIsHashing(true)
    try {
      const response = await blockchainApi.hashDocuments({ documents })
      setHashResults(response)
      setActiveTab('preview')
    } catch (error) {
      console.error('Document hashing failed:', error)
      // Could show error toast here
    } finally {
      setIsHashing(false)
    }
  }

  const handleNotarizationComplete = (result: SubnetNotarizeResponse) => {
    setNotarizationResult(result)
    setActiveTab('result')
  }

  const resetWorkflow = () => {
    setDocuments([])
    setHashResults(null)
    setNotarizationResult(null)
    setActiveTab('documents')
  }

  return (
    <div className="min-h-screen bg-gradient-warm">
      {/* Hero Header */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <div className="flex items-center justify-center mb-6">
            <div className="relative">
              <div className="flex items-center justify-center w-20 h-20 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-elegant animate-glow">
                <Blocks className="h-10 w-10 text-white" />
              </div>
              <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                <CheckCircle className="w-4 h-4 text-white" />
              </div>
            </div>
          </div>
          
          <h1 className="text-4xl md:text-5xl font-display font-bold text-brown-900 tracking-tight mb-6 animate-fadeIn">
            Blockchain Operations
            <span className="block text-2xl md:text-3xl text-blue-600 font-light mt-2">
              Subnet Notarization & Verification
            </span>
          </h1>

          <p className="text-xl text-brown-600 mb-8 max-w-3xl mx-auto leading-relaxed animate-fadeIn" style={{animationDelay: '0.2s'}}>
            Secure document notarization on private Avalanche subnet with cryptographic verification. 
            Enterprise-grade security with server-managed gas fees and transparent cost estimates.
          </p>

          <div className="flex flex-wrap justify-center gap-4 animate-fadeIn" style={{animationDelay: '0.4s'}}>
            <div className="bg-white/80 backdrop-blur-sm px-4 py-2 rounded-lg border border-blue-200 flex items-center space-x-2">
              <Lock className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-700">AES-GCM Encryption</span>
            </div>
            <div className="bg-white/80 backdrop-blur-sm px-4 py-2 rounded-lg border border-green-200 flex items-center space-x-2">
              <Shield className="h-4 w-4 text-green-600" />
              <span className="text-sm font-medium text-green-700">Merkle Tree Proofs</span>
            </div>
            <div className="bg-white/80 backdrop-blur-sm px-4 py-2 rounded-lg border border-purple-200 flex items-center space-x-2">
              <Sparkles className="h-4 w-4 text-purple-600" />
              <span className="text-sm font-medium text-purple-700">Chain ID: 43210</span>
            </div>
          </div>
        </div>
        
        {/* Background decoration */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-10 w-64 h-64 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-full filter blur-3xl animate-float"></div>
          <div className="absolute bottom-20 right-10 w-80 h-80 bg-gradient-to-r from-green-500/20 to-blue-500/20 rounded-full filter blur-3xl animate-float" style={{animationDelay: '3s'}}></div>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-20 space-y-12">

        {/* Blockchain Status */}
        <div className="animate-fadeIn">
          <BlockchainStatus />
        </div>

        {/* Main Workflow */}
        <div className="bg-white/60 backdrop-blur-sm rounded-3xl border border-brown-200 shadow-elegant p-8 animate-fadeIn" style={{animationDelay: '0.2s'}}>
          <div className="text-center mb-8">
            <h2 className="text-3xl font-display font-bold text-brown-900 mb-4">
              Document Notarization Workflow
            </h2>
            <p className="text-brown-600 text-lg max-w-2xl mx-auto">
              Upload documents, preview cryptographic hashes, and notarize on the private Avalanche subnet with full transparency
            </p>
          </div>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-4 bg-brown-50 p-2 rounded-2xl mb-8">
              <TabsTrigger 
                value="documents" 
                className="flex items-center space-x-2 rounded-xl data-[state=active]:bg-white data-[state=active]:shadow-soft data-[state=active]:text-brown-900 transition-all duration-300"
              >
                <FileText className="h-4 w-4" />
                <span className="font-medium">Documents</span>
              </TabsTrigger>
              <TabsTrigger 
                value="preview" 
                disabled={!hashResults}
                className="flex items-center space-x-2 rounded-xl data-[state=active]:bg-white data-[state=active]:shadow-soft data-[state=active]:text-brown-900 transition-all duration-300 disabled:opacity-50"
              >
                <Hash className="h-4 w-4" />
                <span className="font-medium">Preview</span>
              </TabsTrigger>
              <TabsTrigger 
                value="notarize" 
                disabled={!hashResults}
                className="flex items-center space-x-2 rounded-xl data-[state=active]:bg-white data-[state=active]:shadow-soft data-[state=active]:text-brown-900 transition-all duration-300 disabled:opacity-50"
              >
                <Shield className="h-4 w-4" />
                <span className="font-medium">Notarize</span>
              </TabsTrigger>
              <TabsTrigger 
                value="result" 
                disabled={!notarizationResult}
                className="flex items-center space-x-2 rounded-xl data-[state=active]:bg-white data-[state=active]:shadow-soft data-[state=active]:text-brown-900 transition-all duration-300 disabled:opacity-50"
              >
                <Zap className="h-4 w-4" />
                <span className="font-medium">Result</span>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="documents" className="space-y-6">
              <DocumentUploader
                documents={documents}
                onDocumentsChange={setDocuments}
                onHashDocuments={handleHashDocuments}
                isHashing={isHashing}
              />
            </TabsContent>

            <TabsContent value="preview" className="space-y-6">
              {hashResults && (
                <div className="animate-fadeIn">
                  <DocumentHashResults results={hashResults} />
                  <div className="flex justify-center mt-6">
                    <Button
                      onClick={() => setActiveTab('notarize')}
                      className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-medium px-8 py-3"
                    >
                      <ArrowRight className="h-4 w-4 mr-2" />
                      Proceed to Notarization
                    </Button>
                  </div>
                </div>
              )}
            </TabsContent>

            <TabsContent value="notarize" className="space-y-6">
              <div className="animate-fadeIn">
                <NotarizationForm
                  documents={documents}
                  onNotarizationComplete={handleNotarizationComplete}
                />
              </div>
            </TabsContent>

            <TabsContent value="result" className="space-y-6">
              {notarizationResult && (
                <div className="animate-fadeIn">
                  <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-2xl p-8 text-center shadow-soft">
                    <div className="flex items-center justify-center mb-6">
                      <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full flex items-center justify-center animate-glow">
                        <CheckCircle className="h-8 w-8 text-white" />
                      </div>
                    </div>
                    <div className="text-green-700 text-3xl font-display font-bold mb-4">
                      🎉 Notarization Complete!
                    </div>
                    <p className="text-green-600 text-lg mb-8">
                      Your documents have been successfully notarized and secured on the private Avalanche subnet
                    </p>
                    
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                      <Button
                        onClick={resetWorkflow}
                        className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-medium px-8 py-3"
                      >
                        <ArrowRight className="h-4 w-4 mr-2" />
                        Start New Notarization
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => setActiveTab('lookup')}
                        className="border-green-300 text-green-700 hover:bg-green-50 px-8 py-3"
                      >
                        <Search className="h-4 w-4 mr-2" />
                        Verify Result
                      </Button>
                    </div>
                  </div>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>

        {/* Verification Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-fadeIn" style={{animationDelay: '0.4s'}}>
          <Card className="bg-white/80 backdrop-blur-sm border-brown-200 shadow-soft">
            <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-t-xl">
              <CardTitle className="flex items-center space-x-3 text-xl font-display text-brown-900">
                <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg">
                  <Search className="h-5 w-5 text-white" />
                </div>
                <span>Verify Notarization</span>
              </CardTitle>
              <CardDescription className="text-brown-600 text-base">
                Look up and verify existing document notarizations using Run ID
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <NotarizationLookup />
            </CardContent>
          </Card>

          {/* Workflow Progress */}
          <Card className="bg-white/80 backdrop-blur-sm border-brown-200 shadow-soft">
            <CardHeader className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-t-xl">
              <CardTitle className="flex items-center space-x-3 text-xl font-display text-brown-900">
                <div className="p-2 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg">
                  <CheckCircle className="h-5 w-5 text-white" />
                </div>
                <span>Workflow Progress</span>
              </CardTitle>
              <CardDescription className="text-brown-600 text-base">
                Track your document notarization progress
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6 space-y-4">
              <div className={`flex items-center space-x-3 p-3 rounded-lg transition-all duration-300 ${documents.length > 0 ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${documents.length > 0 ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-600'}`}>
                  {documents.length > 0 ? '✓' : '1'}
                </div>
                <div>
                  <div className={`font-medium ${documents.length > 0 ? 'text-green-700' : 'text-gray-600'}`}>
                    Add Documents ({documents.length})
                  </div>
                  <div className="text-sm text-gray-500">Upload or enter document content</div>
                </div>
              </div>
              
              <div className={`flex items-center space-x-3 p-3 rounded-lg transition-all duration-300 ${hashResults ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${hashResults ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-600'}`}>
                  {hashResults ? '✓' : '2'}
                </div>
                <div>
                  <div className={`font-medium ${hashResults ? 'text-green-700' : 'text-gray-600'}`}>
                    Generate Hashes
                  </div>
                  <div className="text-sm text-gray-500">Create cryptographic fingerprints</div>
                </div>
              </div>
              
              <div className={`flex items-center space-x-3 p-3 rounded-lg transition-all duration-300 ${notarizationResult ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${notarizationResult ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-600'}`}>
                  {notarizationResult ? '✓' : '3'}
                </div>
                <div>
                  <div className={`font-medium ${notarizationResult ? 'text-green-700' : 'text-gray-600'}`}>
                    Submit to Subnet
                  </div>
                  <div className="text-sm text-gray-500">Notarize on Avalanche blockchain</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Information Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-fadeIn" style={{animationDelay: '0.6s'}}>
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200 shadow-soft card-hover">
            <CardHeader>
              <CardTitle className="text-blue-800 font-display flex items-center space-x-2">
                <Lock className="h-5 w-5" />
                <span>Cryptographic Integrity</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-blue-700 space-y-3">
              <div className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 mt-0.5 text-blue-600" />
                <div><strong>Merkle Trees:</strong> Tamper-evident document proofs</div>
              </div>
              <div className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 mt-0.5 text-blue-600" />
                <div><strong>Keccak-256:</strong> Ethereum-standard hashing</div>
              </div>
              <div className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 mt-0.5 text-blue-600" />
                <div><strong>Immutable:</strong> Records cannot be altered</div>
              </div>
              <div className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 mt-0.5 text-blue-600" />
                <div><strong>Verifiable:</strong> Anyone can verify integrity</div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200 shadow-soft card-hover">
            <CardHeader>
              <CardTitle className="text-green-800 font-display flex items-center space-x-2">
                <Shield className="h-5 w-5" />
                <span>Private Subnet</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-green-700 space-y-3">
              <div className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 mt-0.5 text-green-600" />
                <div><strong>Avalanche C-Chain:</strong> EVM-compatible subnet</div>
              </div>
              <div className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 mt-0.5 text-green-600" />
                <div><strong>Private Network:</strong> Restricted access control</div>
              </div>
              <div className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 mt-0.5 text-green-600" />
                <div><strong>Low Fees:</strong> Server pays all gas costs</div>
              </div>
              <div className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 mt-0.5 text-green-600" />
                <div><strong>Fast Finality:</strong> Sub-second confirmations</div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200 shadow-soft card-hover">
            <CardHeader>
              <CardTitle className="text-purple-800 font-display flex items-center space-x-2">
                <Sparkles className="h-5 w-5" />
                <span>Encrypted Audit</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-purple-700 space-y-3">
              <div className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 mt-0.5 text-purple-600" />
                <div><strong>AES-GCM:</strong> Authenticated encryption</div>
              </div>
              <div className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 mt-0.5 text-purple-600" />
                <div><strong>Opaque Labels:</strong> Hidden metadata keys</div>
              </div>
              <div className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 mt-0.5 text-purple-600" />
                <div><strong>Full Recovery:</strong> Complete audit trails</div>
              </div>
              <div className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 mt-0.5 text-purple-600" />
                <div><strong>Secure Storage:</strong> On-chain encrypted data</div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}