'use client';

import { useCallback } from 'react';
import { Upload, FileText, Image, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface DocumentUploaderProps {
  onFilesChange: (files: File[]) => void;
}

export function DocumentUploader({ onFilesChange }: DocumentUploaderProps) {
  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    onFilesChange(files);
  }, [onFilesChange]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    onFilesChange(files);
  }, [onFilesChange]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
  }, []);

  return (
    <div 
      className="border-2 border-dashed border-stone-300 rounded-lg p-8 text-center hover:border-brown-500 transition-colors"
      onDrop={handleDrop}
      onDragOver={handleDragOver}
    >
      <div className="flex flex-col items-center space-y-4">
        <div className="p-4 bg-brown-100 rounded-full">
          <Upload className="h-8 w-8 text-brown-700" />
        </div>
        
        <div>
          <h3 className="text-lg font-display font-semibold text-brown-900 mb-2">
            Upload Documents
          </h3>
          <p className="text-brown-500 text-sm mb-4">
            Drag and drop files here, or click to browse
          </p>
          
          <input
            type="file"
            multiple
            accept=".pdf,.docx,.doc,.jpg,.jpeg,.png"
            onChange={handleFileSelect}
            className="hidden"
            id="file-upload"
          />
          <label htmlFor="file-upload">
            <Button type="button" variant="outline" className="border-brown-700 text-brown-700 hover:bg-brown-50">
              Choose Files
            </Button>
          </label>
        </div>
        
        <div className="flex items-center space-x-4 text-sm text-brown-500">
          <div className="flex items-center space-x-1">
            <FileText className="h-4 w-4" />
            <span>PDF, DOCX</span>
          </div>
          <div className="flex items-center space-x-1">
            <Image className="h-4 w-4" />
            <span>JPG, PNG</span>
          </div>
        </div>
      </div>
    </div>
  );
}