'use client';

import { useState, useEffect } from 'react';
import { useUser } from '@clerk/nextjs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { ChatInterface } from './ChatInterface';
import { DocumentViewer } from './DocumentViewer';
import { EvidencePanel } from './EvidencePanel';
import { SubnetNotarization } from './SubnetNotarization';
// import { DocumentUploader } from './DocumentUploader';
import { 
  MessageSquare, 
  FileText, 
  Shield, 
  Download, 
  Share2,
  CheckCircle,
  Clock,
  AlertCircle,
  Loader2,
  ArrowLeft
} from 'lucide-react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import type { Matter, Document, EvidenceItem } from '@/types';

interface MatterWorkspaceProps {
  matterId: string;
  isNewlyCreated?: boolean;
}

export function MatterWorkspace({ matterId, isNewlyCreated }: MatterWorkspaceProps) {
  const { user, isLoaded } = useUser();
  const { toast } = useToast();
  const [matter, setMatter] = useState<Matter | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoadingMatter, setIsLoadingMatter] = useState(true);
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(true);
  const [isProcessing, setIsProcessing] = useState(isNewlyCreated);
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceItem | null>(null);
  const [activeTab, setActiveTab] = useState('chat');
  const [error, setError] = useState<string | null>(null);
  const [currentRunId, setCurrentRunId] = useState<string | null>(null);
  const [isNotarized, setIsNotarized] = useState(false);

  useEffect(() => {
    if (isLoaded && user) {
      loadMatterData();
    }
  }, [isLoaded, user, matterId]);

  useEffect(() => {
    if (isNewlyCreated) {
      // Simulate processing time for newly created matters
      const timer = setTimeout(() => {
        setIsProcessing(false);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [isNewlyCreated]);

  const loadMatterData = async () => {
    try {
      // Load matter details
      const matterResponse = await apiClient.getMatter(matterId);
      if (matterResponse.error) {
        setError(matterResponse.error);
      } else if (matterResponse.data) {
        setMatter(matterResponse.data);
      }
      setIsLoadingMatter(false);

      // Load documents
      const documentsResponse = await apiClient.getDocuments(matterId);
      if (documentsResponse.error) {
        console.warn('Failed to load documents:', documentsResponse.error);
      } else if (documentsResponse.data) {
        setDocuments(documentsResponse.data);
        
        // Check if any documents are still processing
        const hasProcessingDocs = documentsResponse.data.some(doc => 
          doc.ocr_status === 'processing' || doc.ocr_status === 'pending'
        );
        if (hasProcessingDocs && !isNewlyCreated) {
          setIsProcessing(true);
          // Poll for updates
          const pollTimer = setInterval(async () => {
            const updatedDocs = await apiClient.getDocuments(matterId);
            if (updatedDocs.data) {
              setDocuments(updatedDocs.data);
              const stillProcessing = updatedDocs.data.some(doc => 
                doc.ocr_status === 'processing' || doc.ocr_status === 'pending'
              );
              if (!stillProcessing) {
                setIsProcessing(false);
                clearInterval(pollTimer);
              }
            }
          }, 5000);
          
          // Clear polling after 5 minutes
          setTimeout(() => clearInterval(pollTimer), 300000);
        }
      }
      setIsLoadingDocuments(false);
    } catch (err) {
      console.error('Failed to load matter data:', err);
      setError('Failed to load matter data');
      setIsLoadingMatter(false);
      setIsLoadingDocuments(false);
    }
  };

  const handleDocumentUpload = async () => {
    // Refresh documents after upload
    await loadMatterData();
  };

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-cream-50 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-brown-700" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-cream-50 flex items-center justify-center">
        <Card className="w-96">
          <CardHeader>
            <CardTitle className="text-center">Authentication Required</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-center text-muted-foreground">
              Please sign in to access this matter.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isLoadingMatter) {
    return (
      <div className="min-h-screen bg-cream-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="space-y-8">
            <Skeleton className="h-8 w-64" />
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2">
                <Skeleton className="h-96" />
              </div>
              <div>
                <Skeleton className="h-64" />
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !matter) {
    return (
      <div className="min-h-screen bg-cream-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <Link href="/dashboard">
              <Button variant="ghost" className="mb-4 text-brown-600 hover:text-brown-800">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
            </Link>
          </div>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {error || 'Matter not found. Please check the URL and try again.'}
            </AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back Navigation */}
      <div className="mb-6">
        <Link href="/dashboard">
          <Button variant="ghost" className="text-brown-600 hover:text-brown-800">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
        </Link>
      </div>

      {/* Matter Header */}
      <div className="mb-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-brown-900 mb-2">
              {matter.title}
            </h1>
            <div className="flex items-center gap-4">
              <Badge className="bg-olive-400 text-cream-100">
                {matter.status || 'active'}
              </Badge>
              <Badge variant="outline" className="border-brown-500 text-brown-700">
                {matter.language === 'hi' ? 'Hindi' : 'English'}
              </Badge>
              <span className="text-sm text-brown-500 flex items-center gap-1">
                <FileText className="h-4 w-4" />
                {documents.length} documents
              </span>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button variant="outline" className="border-brown-700 text-brown-700">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button variant="outline" className="border-brown-700 text-brown-700">
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </Button>
          </div>
        </div>
      </div>

      {/* Processing Status */}
      {isProcessing && (
        <Card className="mb-8 bg-gold-500/10 border-gold-500">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gold-500"></div>
              <div>
                <h3 className="text-lg font-display font-semibold text-brown-900">
                  Processing Documents
                </h3>
                <p className="text-brown-500">
                  Running OCR analysis and indexing documents for AI research...
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column - Chat and Documents */}
        <div className="lg:col-span-2 space-y-6">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-2 bg-cream-100">
              <TabsTrigger value="chat" className="data-[state=active]:bg-brown-700 data-[state=active]:text-cream-100">
                <MessageSquare className="h-4 w-4 mr-2" />
                Chat Workspace
              </TabsTrigger>
              <TabsTrigger value="documents" className="data-[state=active]:bg-brown-700 data-[state=active]:text-cream-100">
                <FileText className="h-4 w-4 mr-2" />
                Documents
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="chat" className="mt-6">
              <ChatInterface 
                matterId={matterId} 
                disabled={isProcessing}
                onEvidenceSelect={setSelectedEvidence}
                onRunComplete={(runId: string) => {
                  setCurrentRunId(runId);
                  setIsNotarized(false);
                }}
              />
            </TabsContent>
            
            <TabsContent value="documents" className="mt-6">
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FileText className="h-5 w-5" />
                      Upload Documents
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="border-2 border-dashed border-brown-300 rounded-lg p-8 text-center">
                      <FileText className="h-12 w-12 text-brown-400 mx-auto mb-4" />
                      <p className="text-brown-600 mb-4">
                        Upload legal documents related to this matter
                      </p>
                      <Button variant="outline">
                        Select Files
                      </Button>
                    </div>
                  </CardContent>
                </Card>
                <DocumentViewer 
                  matterId={matterId} 
                  documents={documents}
                  isLoading={isLoadingDocuments}
                />
              </div>
            </TabsContent>
          </Tabs>
        </div>

        {/* Right Column - Evidence and Notarization */}
        <div className="space-y-6">
          <EvidencePanel 
            evidence={selectedEvidence}
            onDocumentJump={(docId, paragraph) => {
              setActiveTab('documents');
              // Implement document jump logic
            }}
          />
          
          <SubnetNotarization 
            matterId={matterId}
            isNotarized={isNotarized}
            runId={currentRunId}
            onNotarized={() => setIsNotarized(true)}
          />
        </div>
      </div>
    </div>
  );
}