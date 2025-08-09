'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { FileText, Eye, Download, Search } from 'lucide-react';

interface DocumentViewerProps {
  matterId: string;
}

const mockDocuments = [
  {
    id: '1',
    name: 'Commercial_Contract_Main.pdf',
    type: 'PDF',
    size: '2.4 MB',
    pages: 15,
    status: 'processed',
    lastModified: '2 days ago'
  },
  {
    id: '2',
    name: 'Breach_Notice_Letter.docx',
    type: 'DOCX',
    size: '890 KB',
    pages: 3,
    status: 'processed',
    lastModified: '1 day ago'
  },
  {
    id: '3',
    name: 'Financial_Damages_Report.pdf',
    type: 'PDF',
    size: '1.8 MB',
    pages: 8,
    status: 'processing',
    lastModified: '4 hours ago'
  }
];

export function DocumentViewer({ matterId }: DocumentViewerProps) {
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processed':
        return 'bg-olive-400 text-cream-100';
      case 'processing':
        return 'bg-gold-500 text-brown-900';
      default:
        return 'bg-stone-200 text-brown-700';
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Document List */}
      <Card className="lg:col-span-1 bg-cream-100 border-stone-200">
        <CardHeader>
          <CardTitle className="text-lg font-display text-brown-900 flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Documents ({mockDocuments.length})
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="space-y-1">
            {mockDocuments.map((doc) => (
              <button
                key={doc.id}
                onClick={() => setSelectedDocument(doc.id)}
                className={`w-full p-4 text-left hover:bg-white transition-colors ${
                  selectedDocument === doc.id ? 'bg-white border-r-2 border-brown-700' : ''
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <h4 className="text-sm font-medium text-brown-900 truncate pr-2">
                    {doc.name}
                  </h4>
                  <Badge className={getStatusColor(doc.status)} variant="secondary">
                    {doc.status}
                  </Badge>
                </div>
                <div className="text-xs text-brown-500 space-y-1">
                  <div>{doc.type} • {doc.size} • {doc.pages} pages</div>
                  <div>Modified {doc.lastModified}</div>
                </div>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Document Viewer */}
      <Card className="lg:col-span-2 bg-cream-100 border-stone-200">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-display text-brown-900">
              {selectedDocument 
                ? mockDocuments.find(d => d.id === selectedDocument)?.name 
                : 'Select a document to view'
              }
            </CardTitle>
            {selectedDocument && (
              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="text-brown-700">
                  <Search className="h-4 w-4 mr-2" />
                  Search
                </Button>
                <Button variant="outline" size="sm" className="text-brown-700">
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {selectedDocument ? (
            <div className="bg-white rounded-lg border border-stone-200 h-[500px] flex items-center justify-center">
              <div className="text-center text-brown-500">
                <FileText className="h-16 w-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg font-display mb-2">Document Viewer</p>
                <p className="text-sm">
                  In a real implementation, this would show the PDF/document content
                  <br />
                  with highlighting for cited paragraphs and evidence anchors.
                </p>
              </div>
            </div>
          ) : (
            <div className="h-[500px] flex items-center justify-center text-brown-500">
              <div className="text-center">
                <Eye className="h-16 w-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg font-display">No document selected</p>
                <p className="text-sm">Choose a document from the list to view it here</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}