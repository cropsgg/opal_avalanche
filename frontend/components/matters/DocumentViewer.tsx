'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { FileText, Eye, Download, Search, Clock, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import type { Document } from '@/types';

interface DocumentViewerProps {
  matterId: string;
  documents: Document[];
  isLoading: boolean;
}

export function DocumentViewer({ matterId, documents, isLoading }: DocumentViewerProps) {
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500 text-white';
      case 'processing':
        return 'bg-gold-500 text-brown-900';
      case 'pending':
        return 'bg-blue-500 text-white';
      case 'failed':
        return 'bg-red-500 text-white';
      default:
        return 'bg-stone-200 text-brown-700';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return CheckCircle;
      case 'processing':
        return Loader2;
      case 'pending':
        return Clock;
      case 'failed':
        return AlertCircle;
      default:
        return FileText;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileName = (path: string) => {
    return path.split('/').pop() || path;
  };

  const formatLastModified = (dateString: string) => {
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true });
    } catch {
      return 'Recently';
    }
  };

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-1 bg-cream-100 border-stone-200">
          <CardHeader>
            <CardTitle className="text-lg font-display text-brown-900 flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Documents
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-3 w-2/3" />
              </div>
            ))}
          </CardContent>
        </Card>
        <Card className="lg:col-span-2 bg-cream-100 border-stone-200">
          <CardHeader>
            <Skeleton className="h-6 w-48" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-96 w-full" />
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Document List */}
      <Card className="lg:col-span-1 bg-cream-100 border-stone-200">
        <CardHeader>
          <CardTitle className="text-lg font-display text-brown-900 flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Documents ({documents.length})
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {documents.length === 0 ? (
            <div className="p-8 text-center">
              <FileText className="h-12 w-12 text-brown-400 mx-auto mb-4" />
              <p className="text-brown-500 font-medium mb-2">No documents uploaded</p>
              <p className="text-sm text-brown-400">Upload documents to get started</p>
            </div>
          ) : (
            <div className="space-y-1">
              {documents.map((doc) => {
                const StatusIcon = getStatusIcon(doc.ocr_status);
                return (
                  <button
                    key={doc.id}
                    onClick={() => setSelectedDocument(doc.id)}
                    className={`w-full p-4 text-left hover:bg-white transition-colors ${
                      selectedDocument === doc.id ? 'bg-white border-r-2 border-brown-700' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="text-sm font-medium text-brown-900 truncate pr-2">
                        {getFileName(doc.storage_path)}
                      </h4>
                      <div className="flex items-center gap-2">
                        <StatusIcon 
                          className={`h-4 w-4 ${
                            doc.ocr_status === 'processing' ? 'animate-spin' : ''
                          }`} 
                        />
                        <Badge className={getStatusColor(doc.ocr_status)} variant="secondary">
                          {doc.ocr_status}
                        </Badge>
                      </div>
                    </div>
                    <div className="text-xs text-brown-500 space-y-1">
                      <div>
                        {doc.filetype.toUpperCase()} • {formatFileSize(doc.size)}
                      </div>
                      <div>
                        Uploaded {formatLastModified(doc.created_at)}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Document Viewer */}
      <Card className="lg:col-span-2 bg-cream-100 border-stone-200">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-display text-brown-900">
              {selectedDocument 
                ? getFileName(documents.find(d => d.id === selectedDocument)?.storage_path || '') 
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