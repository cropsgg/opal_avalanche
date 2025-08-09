'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ArrowRight, FileText, AlertCircle, Loader2 } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

interface DocumentUploaderProps {
  onFilesChange: (files: File[]) => void;
}

function DocumentUploader({ onFilesChange }: DocumentUploaderProps) {
  const [files, setFiles] = useState<File[]>([]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    setFiles(selectedFiles);
    onFilesChange(selectedFiles);
  };

  return (
    <div className="space-y-4">
      <input
        type="file"
        multiple
        accept=".pdf,.docx,.doc,.png,.jpg,.jpeg"
        onChange={handleFileChange}
        className="block w-full text-sm text-brown-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-brown-50 file:text-brown-700 hover:file:bg-brown-100"
      />
      {files.length > 0 && (
        <div className="text-sm text-brown-600">
          {files.length} file(s) selected: {files.map(f => f.name).join(', ')}
        </div>
      )}
    </div>
  );
}

export function MatterCreationForm() {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    language: 'en',
    jurisdiction: ''
  });
  const [documents, setDocuments] = useState<File[]>([]);
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsCreating(true);
    setError(null);

    try {
      // Create matter first
      const matterResponse = await apiClient.createMatter({
        title: formData.title,
        language: formData.language
      });

      if (matterResponse.error) {
        setError(matterResponse.error);
        toast({
          title: 'Error',
          description: matterResponse.error,
          variant: 'destructive'
        });
        return;
      }

      const matterId = matterResponse.data?.id;
      if (!matterId) {
        setError('Failed to create matter');
        return;
      }

      // Upload documents if any
      if (documents.length > 0) {
        let uploadErrors = 0;
        for (const file of documents) {
          const uploadResponse = await apiClient.uploadDocument(matterId, file);
          if (uploadResponse.error) {
            uploadErrors++;
            console.error(`Failed to upload ${file.name}:`, uploadResponse.error);
          }
        }

        if (uploadErrors > 0) {
          toast({
            title: 'Partial Upload Success',
            description: `${documents.length - uploadErrors} of ${documents.length} files uploaded successfully.`,
            variant: 'default'
          });
        } else {
          toast({
            title: 'Success',
            description: 'Matter created and all documents uploaded successfully.',
          });
        }
      } else {
        toast({
          title: 'Success',
          description: 'Matter created successfully.',
        });
      }

      // Redirect to the matter workspace
      router.push(`/matters/${matterId}?created=true`);
    } catch (err) {
      console.error('Matter creation failed:', err);
      setError('An unexpected error occurred');
      toast({
        title: 'Error',
        description: 'Failed to create matter. Please try again.',
        variant: 'destructive'
      });
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Matter Information */}
      <Card className="bg-cream-100 border-stone-200">
        <CardHeader>
          <CardTitle className="text-xl font-display text-brown-900">
            Matter Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="title" className="text-brown-700">Matter Title</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="e.g., Contract Dispute Analysis"
              className="mt-1"
              required
              disabled={isCreating}
            />
          </div>
          
          <div>
            <Label htmlFor="description" className="text-brown-700">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Brief description of the legal matter..."
              className="mt-1"
              rows={3}
              disabled={isCreating}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="language" className="text-brown-700">Document Language</Label>
              <Select 
                value={formData.language}
                onValueChange={(value) => setFormData({ ...formData, language: value })}
                disabled={isCreating}
              >
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select language" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="hi">Hindi (हिंदी)</SelectItem>
                  <SelectItem value="mixed">Mixed Languages</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="jurisdiction" className="text-brown-700">Jurisdiction</Label>
              <Select 
                value={formData.jurisdiction}
                onValueChange={(value) => setFormData({ ...formData, jurisdiction: value })}
                disabled={isCreating}
              >
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select jurisdiction" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="supreme-court">Supreme Court of India</SelectItem>
                  <SelectItem value="delhi-hc">Delhi High Court</SelectItem>
                  <SelectItem value="mumbai-hc">Bombay High Court</SelectItem>
                  <SelectItem value="bangalore-hc">Karnataka High Court</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Document Upload */}
      <Card className="bg-cream-100 border-stone-200">
        <CardHeader>
          <CardTitle className="text-xl font-display text-brown-900 flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Document Upload
          </CardTitle>
        </CardHeader>
        <CardContent>
          <DocumentUploader onFilesChange={setDocuments} />
          {documents.length > 0 && (
            <div className="mt-4 p-4 bg-white rounded-md border border-stone-200">
              <p className="text-sm text-brown-700 mb-2">
                {documents.length} file(s) selected for analysis
              </p>
              <div className="text-xs text-brown-500">
                Maximum 50MB per file, 100 files per matter
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Submit */}
      <div className="flex justify-end">
        <Button 
          type="submit" 
          size="lg" 
          disabled={!formData.title || !formData.language || isCreating}
          className="bg-brown-700 hover:bg-brown-500 text-cream-100 border border-gold-500"
        >
          {isCreating ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Creating Matter...
            </>
          ) : (
            <>
              Create Matter
              <ArrowRight className="ml-2 h-4 w-4" />
            </>
          )}
        </Button>
      </div>
    </form>
  );
}