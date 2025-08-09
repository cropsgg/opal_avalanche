'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { FileText, ExternalLink, Pin, GitCompare as Compare, Filter } from 'lucide-react';

interface EvidencePanelProps {
  evidence: any;
  onDocumentJump: (docId: string, paragraph: string) => void;
}

const mockCitations = [
  {
    id: '1',
    case: 'Hadley v Baxendale',
    citation: '(1854) 9 Exch 341',
    court: 'Court of Exchequer',
    year: '1854',
    judge: 'Baron Alderson',
    relevance: 'High',
    paragraphs: ['23', '24', '25'],
    snippet: 'The damages which the other party ought to receive in respect of such breach of contract should be such as may fairly and reasonably be considered...',
    pinned: false
  },
  {
    id: '2',
    case: 'Victoria Laundry v Newman Industries',
    citation: '[1949] 2 KB 528',
    court: 'Court of Appeal',
    year: '1949',
    judge: 'Lord Asquith',
    relevance: 'High',
    paragraphs: ['15', '16'],
    snippet: 'It is well settled that the governing purpose of damages is to put the party whose rights have been violated in the same position...',
    pinned: true
  },
  {
    id: '3',
    case: 'Koufos v Czarnikow Ltd',
    citation: '[1969] 1 AC 350',
    court: 'House of Lords',
    year: '1969',
    judge: 'Lord Reid',
    relevance: 'Medium',
    paragraphs: ['42'],
    snippet: 'The question for decision is whether a plaintiff can recover as damages for breach of contract a loss of a kind which the defendant...',
    pinned: false
  }
];

export function EvidencePanel({ evidence, onDocumentJump }: EvidencePanelProps) {
  const getRelevanceBadge = (relevance: string) => {
    switch (relevance.toLowerCase()) {
      case 'high':
        return 'bg-olive-400 text-cream-100';
      case 'medium':
        return 'bg-gold-500 text-brown-900';
      case 'low':
        return 'bg-stone-200 text-brown-700';
      default:
        return 'bg-stone-200 text-brown-700';
    }
  };

  return (
    <Card className="bg-cream-100 border-stone-200">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-display text-brown-900 flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Citations & Evidence
          </CardTitle>
          <Button variant="outline" size="sm" className="text-brown-700">
            <Filter className="h-4 w-4 mr-2" />
            Filter
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {mockCitations.map((citation) => (
          <div key={citation.id} className="bg-white rounded-lg border border-stone-200 p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <h4 className="font-display font-semibold text-brown-900 mb-1">
                  {citation.case}
                </h4>
                <div className="flex items-center gap-2 mb-2">
                  <Badge className={getRelevanceBadge(citation.relevance)} variant="secondary">
                    {citation.relevance}
                  </Badge>
                  <span className="text-sm text-brown-500">{citation.citation}</span>
                </div>
                <div className="text-xs text-brown-500 space-y-1">
                  <div>{citation.court} • {citation.year} • {citation.judge}</div>
                  <div>Paragraphs: {citation.paragraphs.join(', ')}</div>
                </div>
              </div>
              <div className="flex gap-1">
                <Button variant="ghost" size="icon" className="h-8 w-8 text-brown-500">
                  {citation.pinned ? (
                    <Pin className="h-4 w-4 fill-current" />
                  ) : (
                    <Pin className="h-4 w-4" />
                  )}
                </Button>
                <Button variant="ghost" size="icon" className="h-8 w-8 text-brown-500">
                  <Compare className="h-4 w-4" />
                </Button>
              </div>
            </div>
            
            <p className="text-sm text-brown-700 mb-3 italic leading-relaxed">
              "{citation.snippet}"
            </p>
            
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                size="sm" 
                className="text-brown-700 text-xs"
                onClick={() => onDocumentJump('doc1', citation.paragraphs[0])}
              >
                <ExternalLink className="h-3 w-3 mr-1" />
                View in Document
              </Button>
              <Button variant="outline" size="sm" className="text-brown-700 text-xs">
                Full Text
              </Button>
            </div>
          </div>
        ))}
        
        {mockCitations.length === 0 && (
          <div className="text-center py-8 text-brown-500">
            <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p className="font-display mb-2">No evidence selected</p>
            <p className="text-sm">
              Click on evidence buttons in the chat to view citations and supporting documents
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}