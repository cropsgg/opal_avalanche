'use client';

import { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Upload,
  FileText,
  Image,
  X,
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react';
import { apiClient } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { SUPPORTED_FILE_TYPES, MAX_FILE_SIZE } from '@/types';

interface DocumentUploaderProps {
  matterId: string;
  onUploadComplete: () => void;
}

interface UploadFile {
  file: File;
  id: string;
  status: 'pending' | 'uploading' | 'success' | 'error';
  progress: number;
  error?: string | null;
}

export function DocumentUploader({ matterId, onUploadComplete }: DocumentUploaderProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();
  const [uploadFiles, setUploadFiles] = useState<UploadFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);

  const getFileIcon = (fileType: string) => {
    if (fileType.startsWith('image/')) {
      return Image;
    }
    return FileText;
  };

  const validateFile = (file: File): string | null => {
    if (!SUPPORTED_FILE_TYPES.includes(file.type as any)) {
      return `File type ${file.type} is not supported. Please upload PDF, DOCX, or image files.`;
    }

    if (file.size > MAX_FILE_SIZE) {
      return `File size exceeds 50MB limit. Please compress or split the file.`;
    }

    return null;
  };

  const handleFileSelect = (files: FileList | null) => {
    if (!files) return;

    const newFiles: UploadFile[] = Array.from(files).map(file => {
      const error = validateFile(file);
      return {
        file,
        id: `${file.name}-${Date.now()}`,
        status: error ? 'error' : 'pending',
        progress: 0,
        error
      };
    });

    setUploadFiles(prev => [...prev, ...newFiles]);
  };

  const uploadFile = async (uploadFile: UploadFile) => {
    if (uploadFile.status !== 'pending') return;

    setUploadFiles(prev => prev.map(f =>
      f.id === uploadFile.id
        ? { ...f, status: 'uploading', progress: 0 }
        : f
    ));

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setUploadFiles(prev => prev.map(f =>
          f.id === uploadFile.id && f.progress < 90
            ? { ...f, progress: f.progress + 10 }
            : f
        ));
      }, 200);

      const response = await apiClient.uploadDocument(matterId, uploadFile.file);

      clearInterval(progressInterval);

      if (response.error) {
        setUploadFiles(prev => prev.map(f =>
          f.id === uploadFile.id
            ? { ...f, status: 'error', progress: 0, error: response.error }
            : f
        ));
        toast({
          title: 'Upload Failed',
          description: response.error,
          variant: 'destructive'
        });
      } else {
        setUploadFiles(prev => prev.map(f =>
          f.id === uploadFile.id
            ? { ...f, status: 'success', progress: 100 }
            : f
        ));
        toast({
          title: 'Upload Successful',
          description: `${uploadFile.file.name} has been uploaded and is being processed.`
        });
      }
    } catch (error) {
      setUploadFiles(prev => prev.map(f =>
        f.id === uploadFile.id
          ? { ...f, status: 'error', progress: 0, error: 'Upload failed' }
          : f
      ));
      toast({
        title: 'Upload Failed',
        description: 'An unexpected error occurred',
        variant: 'destructive'
      });
    }
  };

  const uploadAllFiles = async () => {
    const pendingFiles = uploadFiles.filter(f => f.status === 'pending');

    for (const file of pendingFiles) {
      await uploadFile(file);
    }

    // Refresh the parent component after all uploads
    onUploadComplete();
  };

  const removeFile = (id: string) => {
    setUploadFiles(prev => prev.filter(f => f.id !== id));
  };

  const clearCompleted = () => {
    setUploadFiles(prev => prev.filter(f => f.status === 'uploading'));
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const hasUploading = uploadFiles.some(f => f.status === 'uploading');
  const hasPending = uploadFiles.some(f => f.status === 'pending');
  const hasCompleted = uploadFiles.some(f => f.status === 'success' || f.status === 'error');

  return (
    <Card className="bg-white border-stone-200">
      <CardHeader>
        <CardTitle className="text-xl  text-brown-900 flex items-center gap-2">
          <Upload className="h-5 w-5" />
          Upload Documents
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Upload Area */}
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            isDragging
              ? 'border-brown-500 bg-brown-50'
              : 'border-stone-300 hover:border-brown-400 hover:bg-stone-50'
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <Upload className="h-12 w-12 text-brown-400 mx-auto mb-4" />
          <p className="text-lg font-medium text-brown-900 mb-2">
            Upload legal documents
          </p>
          <p className="text-sm text-brown-500 mb-4">
            Drag and drop files here, or click to browse
          </p>
          <Button
            onClick={() => fileInputRef.current?.click()}
            className="bg-brown-700 hover:bg-brown-600 text-cream-100"
            disabled={hasUploading}
          >
            Select Files
          </Button>
          <p className="text-xs text-brown-400 mt-4">
            Supports PDF, DOCX, PNG, JPG • Max 50MB per file
          </p>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.doc,.png,.jpg,.jpeg"
          onChange={(e) => handleFileSelect(e.target.files)}
          className="hidden"
        />

        {/* File List */}
        {uploadFiles.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-medium text-brown-900">
                Files ({uploadFiles.length})
              </h3>
              {hasCompleted && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearCompleted}
                  className="text-brown-600"
                >
                  Clear Completed
                </Button>
              )}
            </div>

            <div className="space-y-3">
              {uploadFiles.map((uploadFile) => {
                const Icon = getFileIcon(uploadFile.file.type);
                return (
                  <div
                    key={uploadFile.id}
                    className="flex items-center space-x-4 p-4 border border-stone-200 rounded-lg"
                  >
                    <Icon className="h-8 w-8 text-brown-600 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-brown-900 truncate">
                        {uploadFile.file.name}
                      </p>
                      <p className="text-xs text-brown-500">
                        {(uploadFile.file.size / 1024 / 1024).toFixed(2)} MB
                      </p>

                      {uploadFile.status === 'uploading' && (
                        <div className="mt-2">
                          <Progress value={uploadFile.progress} className="h-2" />
                        </div>
                      )}

                      {uploadFile.error && (
                        <p className="text-xs text-red-600 mt-1">
                          {uploadFile.error}
                        </p>
                      )}
                    </div>

                    <div className="flex items-center space-x-2">
                      {uploadFile.status === 'uploading' && (
                        <Loader2 className="h-4 w-4 animate-spin text-brown-600" />
                      )}
                      {uploadFile.status === 'success' && (
                        <CheckCircle className="h-4 w-4 text-green-600" />
                      )}
                      {uploadFile.status === 'error' && (
                        <AlertCircle className="h-4 w-4 text-red-600" />
                      )}
                      {(uploadFile.status === 'pending' || uploadFile.status === 'error') && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFile(uploadFile.id)}
                          className="text-brown-500 hover:text-red-600"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {hasPending && (
              <div className="flex justify-end">
                <Button
                  onClick={uploadAllFiles}
                  disabled={hasUploading}
                  className="bg-brown-700 hover:bg-brown-600 text-cream-100"
                >
                  {hasUploading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Uploading...
                    </>
                  ) : (
                    'Upload All Files'
                  )}
                </Button>
              </div>
            )}
          </div>
        )}

        {/* Help Text */}
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Documents will be automatically processed with OCR if needed.
            Processing may take a few minutes for scanned documents.
          </AlertDescription>
        </Alert>
      </CardContent>
    </Card>
  );
}
