'use client'

import React, { useState, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { X, Plus, FileText, Upload, Hash } from 'lucide-react'
import { Document } from '@/types'

interface DocumentUploaderProps {
  documents: Document[]
  onDocumentsChange: (documents: Document[]) => void
  onHashDocuments?: () => void
  isHashing?: boolean
}

export default function DocumentUploader({
  documents,
  onDocumentsChange,
  onHashDocuments,
  isHashing = false
}: DocumentUploaderProps) {
  const [newDoc, setNewDoc] = useState<Document>({
    title: '',
    content: '',
    metadata: {}
  })

  const addDocument = useCallback(() => {
    if (!newDoc.content.trim()) return

    const doc: Document = {
      title: (newDoc.title || '').trim() || `Document ${documents.length + 1}`,
      content: newDoc.content.trim(),
      metadata: newDoc.metadata || {}
    }

    onDocumentsChange([...documents, doc])
    setNewDoc({ title: '', content: '', metadata: {} })
  }, [newDoc, documents, onDocumentsChange])

  const removeDocument = useCallback((index: number) => {
    const updated = documents.filter((_, i) => i !== index)
    onDocumentsChange(updated)
  }, [documents, onDocumentsChange])

  const updateDocument = useCallback((index: number, field: keyof Document, value: any) => {
    const updated = documents.map((doc, i) => 
      i === index ? { ...doc, [field]: value } : doc
    )
    onDocumentsChange(updated)
  }, [documents, onDocumentsChange])

  const handleFileUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files) return

    Array.from(files).forEach(file => {
      const reader = new FileReader()
      reader.onload = (e) => {
        const content = e.target?.result as string
        if (content) {
          const doc: Document = {
            title: file.name,
            content,
            metadata: {
              filename: file.name,
              size: file.size,
              type: file.type,
              lastModified: new Date(file.lastModified).toISOString()
            }
          }
          onDocumentsChange([...documents, doc])
        }
      }
      reader.readAsText(file)
    })

    // Reset input
    event.target.value = ''
  }, [documents, onDocumentsChange])

  const getTotalCharacters = () => {
    return documents.reduce((total, doc) => total + doc.content.length, 0)
  }

  return (
    <div className="space-y-6">
      {/* Document List */}
      {documents.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span className="flex items-center space-x-2">
                <FileText className="h-5 w-5" />
                <span>Documents ({documents.length})</span>
              </span>
              <div className="flex items-center space-x-2">
                <Badge variant="outline">
                  {getTotalCharacters().toLocaleString()} characters
                </Badge>
                {onHashDocuments && (
                  <Button
                    onClick={onHashDocuments}
                    disabled={isHashing || documents.length === 0}
                    size="sm"
                    variant="outline"
                  >
                    <Hash className="h-4 w-4 mr-2" />
                    {isHashing ? 'Hashing...' : 'Hash Documents'}
                  </Button>
                )}
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {documents.map((doc, index) => (
              <div key={index} className="border rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <Input
                    value={doc.title}
                    onChange={(e) => updateDocument(index, 'title', e.target.value)}
                    placeholder={`Document ${index + 1}`}
                    className="flex-1 mr-2"
                  />
                  <Button
                    onClick={() => removeDocument(index)}
                    variant="outline"
                    size="sm"
                    className="text-red-600 hover:text-red-700"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
                
                <Textarea
                  value={doc.content}
                  onChange={(e) => updateDocument(index, 'content', e.target.value)}
                  placeholder="Document content..."
                  rows={6}
                  className="resize-y"
                />
                
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <span>{doc.content.length} characters</span>
                  {doc.metadata?.filename && (
                    <span>File: {doc.metadata.filename}</span>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Add Document */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Plus className="h-5 w-5" />
            <span>Add Document</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* File Upload */}
          <div>
            <label htmlFor="file-upload" className="cursor-pointer">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
                <Upload className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                <p className="text-sm text-gray-600">
                  Drop files here or click to upload
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Supports .txt, .md, and other text files
                </p>
              </div>
            </label>
            <input
              id="file-upload"
              type="file"
              multiple
              accept=".txt,.md,.json,.xml,.html,.csv"
              onChange={handleFileUpload}
              className="hidden"
            />
          </div>

          {/* Manual Entry */}
          <div className="border-t pt-4">
            <div className="space-y-3">
              <Input
                value={newDoc.title}
                onChange={(e) => setNewDoc(prev => ({ ...prev, title: e.target.value }))}
                placeholder="Document title (optional)"
              />
              
              <Textarea
                value={newDoc.content}
                onChange={(e) => setNewDoc(prev => ({ ...prev, content: e.target.value }))}
                placeholder="Enter document content..."
                rows={8}
                className="resize-y"
              />
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">
                  {newDoc.content.length} characters
                </span>
                <Button
                  onClick={addDocument}
                  disabled={!newDoc.content.trim()}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Document
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
