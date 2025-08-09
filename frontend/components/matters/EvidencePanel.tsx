'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  FileText, 
  ExternalLink, 
  Pin, 
  GitCompare as Compare, 
  Filter, 
  Scale,
  Calendar,
  MapPin,
  User,
  BookOpen,
  Star,
  Info
} from 'lucide-react';
import type { EvidenceItem } from '@/types';

interface EvidencePanelProps {
  evidence: EvidenceItem | null;
  onDocumentJump: (docId: string, paragraph: string) => void;
}

export function EvidencePanel({ evidence, onDocumentJump }: EvidencePanelProps) {
  const [isPinned, setIsPinned] = useState(false);
  const [activeTab, setActiveTab] = useState('details');
  const getRelevanceBadge = (relevance: string) => {
    switch (relevance.toLowerCase()) {
      case 'high':
        return 'bg-green-500 text-white';
      case 'medium':
        return 'bg-yellow-500 text-black';
      case 'low':
        return 'bg-gray-400 text-white';
      default:
        return 'bg-stone-200 text-brown-700';
    }
  };

  const getRelevanceIcon = (relevance: string) => {
    switch (relevance.toLowerCase()) {
      case 'high':
        return <Star className="h-3 w-3 fill-current" />;
      case 'medium':
        return <Star className="h-3 w-3" />;
      case 'low':
        return <Info className="h-3 w-3" />;
      default:
        return <Info className="h-3 w-3" />;
    }
  };

  if (!evidence) {
    return (
      <Card className="bg-cream-100 border-stone-200">
        <CardHeader>
          <CardTitle className="text-lg font-display text-brown-900 flex items-center gap-2">
            <Scale className="h-5 w-5" />
            Evidence Panel
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12 text-brown-500">
            <Scale className="h-16 w-16 mx-auto mb-4 opacity-50" />
            <h3 className="text-lg font-display font-semibold mb-2">No Evidence Selected</h3>
            <p className="text-sm mb-4">
              Click on citation buttons in the chat to view detailed legal evidence and supporting documents
            </p>
            <div className="flex flex-wrap gap-2 justify-center text-xs">
              <Badge variant="outline">Case Law</Badge>
              <Badge variant="outline">Statutes</Badge>
              <Badge variant="outline">Legal Precedents</Badge>
              <Badge variant="outline">Supporting Documents</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-cream-100 border-stone-200">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-display text-brown-900 flex items-center gap-2">
            <Scale className="h-5 w-5" />
            Legal Evidence
          </CardTitle>
          <div className="flex gap-2">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setIsPinned(!isPinned)}
              className={`text-brown-700 ${isPinned ? 'bg-brown-100' : ''}`}
            >
              <Pin className={`h-4 w-4 ${isPinned ? 'fill-current' : ''}`} />
            </Button>
            <Button variant="outline" size="sm" className="text-brown-700">
              <Compare className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Main Evidence Card */}
        <div className="bg-white rounded-lg border border-stone-200 p-4">
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h3 className="text-lg font-display font-bold text-brown-900 mb-2">
                {evidence.case}
              </h3>
              <div className="flex items-center gap-2 mb-2">
                <Badge className={getRelevanceBadge(evidence.relevance)} variant="secondary">
                  {getRelevanceIcon(evidence.relevance)}
                  <span className="ml-1">{evidence.relevance} Relevance</span>
                </Badge>
                <Badge variant="outline" className="border-brown-300 text-brown-700">
                  {evidence.court}
                </Badge>
              </div>
              <div className="text-sm font-medium text-brown-600 mb-1">
                {evidence.citation}
              </div>
            </div>
          </div>

          {/* Tabs for detailed information */}
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-3 bg-stone-100">
              <TabsTrigger value="details" className="text-xs">Details</TabsTrigger>
              <TabsTrigger value="paragraphs" className="text-xs">Paragraphs</TabsTrigger>
              <TabsTrigger value="analysis" className="text-xs">Analysis</TabsTrigger>
            </TabsList>
            
            <TabsContent value="details" className="mt-4 space-y-3">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4 text-brown-500" />
                    <span className="font-medium">Court:</span>
                  </div>
                  <p className="text-brown-700 ml-6">{evidence.court}</p>
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-brown-500" />
                    <span className="font-medium">Date:</span>
                  </div>
                  <p className="text-brown-700 ml-6">{evidence.date || 'Not specified'}</p>
                </div>
              </div>
              
              {evidence.snippet && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <BookOpen className="h-4 w-4 text-brown-500" />
                    <span className="font-medium">Key Extract:</span>
                  </div>
                  <blockquote className="italic text-brown-700 bg-stone-50 p-3 rounded border-l-4 border-brown-300 ml-6">
                    &quot;{evidence.snippet}&quot;
                  </blockquote>
                </div>
              )}
            </TabsContent>
            
            <TabsContent value="paragraphs" className="mt-4">
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-sm font-medium">
                  <FileText className="h-4 w-4 text-brown-500" />
                  Referenced Paragraphs ({evidence.paragraphs.length})
                </div>
                
                <div className="space-y-2">
                  {evidence.paragraphs.map((para, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-stone-50 rounded">
                      <span className="text-sm font-mono">Paragraph {para}</span>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="text-xs"
                        onClick={() => onDocumentJump(evidence.authority_id, para)}
                      >
                        <ExternalLink className="h-3 w-3 mr-1" />
                        View
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="analysis" className="mt-4">
              <div className="space-y-4">
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    This case is highly relevant to your query based on legal precedent analysis 
                    and contextual similarity to your matter.
                  </AlertDescription>
                </Alert>
                
                <div className="space-y-2">
                  <h4 className="font-medium text-brown-900">Legal Significance:</h4>
                  <ul className="text-sm text-brown-700 space-y-1 ml-4">
                    <li>• Establishes binding precedent in {evidence.court}</li>
                    <li>• Relevant to contract law and damages assessment</li>
                    <li>• Frequently cited in subsequent judgments</li>
                  </ul>
                </div>
              </div>
            </TabsContent>
          </Tabs>

          {/* Action Buttons */}
          <div className="flex gap-2 mt-4 pt-4 border-t border-stone-200">
            <Button 
              variant="outline" 
              size="sm" 
              className="text-brown-700 flex-1"
              onClick={() => onDocumentJump(evidence.authority_id, evidence.paragraphs[0])}
            >
              <ExternalLink className="h-3 w-3 mr-1" />
              Open in Viewer
            </Button>
            <Button variant="outline" size="sm" className="text-brown-700">
              <BookOpen className="h-3 w-3 mr-1" />
              Full Text
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}