'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { DocumentUploader } from './DocumentUploader';
import { ArrowRight, FileText } from 'lucide-react';

export function MatterCreationForm() {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    language: '',
    jurisdiction: ''
  });
  const [documents, setDocuments] = useState<File[]>([]);
  const [isCreating, setIsCreating] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsCreating(true);

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Simulate successful creation and redirect
    router.push('/matters/1?created=true');
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
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
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="language" className="text-brown-700">Document Language</Label>
              <Select onValueChange={(value) => setFormData({ ...formData, language: value })}>
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select language" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="english">English</SelectItem>
                  <SelectItem value="hindi">Hindi (हिंदी)</SelectItem>
                  <SelectItem value="mixed">Mixed Languages</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="jurisdiction" className="text-brown-700">Jurisdiction</Label>
              <Select onValueChange={(value) => setFormData({ ...formData, jurisdiction: value })}>
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
          disabled={!formData.title || !formData.language || documents.length === 0 || isCreating}
          className="bg-brown-700 hover:bg-brown-500 text-cream-100 border border-gold-500"
        >
          {isCreating ? (
            'Creating Matter...'
          ) : (
            <>
              Create Matter & Start Analysis
              <ArrowRight className="ml-2 h-4 w-4" />
            </>
          )}
        </Button>
      </div>
    </form>
  );
}