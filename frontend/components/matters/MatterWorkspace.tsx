'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ChatInterface } from './ChatInterface';
import { DocumentViewer } from './DocumentViewer';
import { EvidencePanel } from './EvidencePanel';
import { Notarization } from './Notarization';
import { 
  MessageSquare, 
  FileText, 
  Shield, 
  Download, 
  Share2,
  CheckCircle,
  Clock
} from 'lucide-react';

interface MatterWorkspaceProps {
  matterId: string;
  isNewlyCreated?: boolean;
}

// Mock matter data
const mockMatter = {
  id: '1',
  title: 'Contract Dispute Analysis',
  status: 'active',
  language: 'English',
  description: 'Commercial contract breach analysis with damages assessment',
  documentsCount: 12,
  lastAnalysis: '2 hours ago',
  notarized: false,
  runId: null
};

export function MatterWorkspace({ matterId, isNewlyCreated }: MatterWorkspaceProps) {
  const [isProcessing, setIsProcessing] = useState(isNewlyCreated);
  const [selectedEvidence, setSelectedEvidence] = useState<any>(null);
  const [activeTab, setActiveTab] = useState('chat');

  useEffect(() => {
    if (isNewlyCreated) {
      // Simulate processing time for newly created matters
      const timer = setTimeout(() => {
        setIsProcessing(false);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [isNewlyCreated]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Matter Header */}
      <div className="mb-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-brown-900 mb-2">
              {mockMatter.title}
            </h1>
            <div className="flex items-center gap-4">
              <Badge className="bg-olive-400 text-cream-100">
                {mockMatter.status}
              </Badge>
              <Badge variant="outline" className="border-brown-500 text-brown-700">
                {mockMatter.language}
              </Badge>
              <span className="text-sm text-brown-500 flex items-center gap-1">
                <FileText className="h-4 w-4" />
                {mockMatter.documentsCount} documents
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
              />
            </TabsContent>
            
            <TabsContent value="documents" className="mt-6">
              <DocumentViewer matterId={matterId} />
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
          
          <Notarization 
            matterId={matterId}
            isNotarized={mockMatter.notarized}
            runId={mockMatter.runId}
          />
        </div>
      </div>
    </div>
  );
}