'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '@clerk/nextjs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ArrowLeft, Plus, Loader2, AlertCircle } from 'lucide-react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

export default function NewMatterPage() {
  const router = useRouter();
  const { user, isLoaded } = useUser();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    language: 'en' as 'en' | 'hi',
    description: ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate form
    const newErrors: Record<string, string> = {};
    if (!formData.title.trim()) {
      newErrors.title = 'Matter title is required';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsLoading(true);
    setErrors({});

    try {
      const response = await apiClient.createMatter({
        title: formData.title.trim(),
        language: formData.language
      });

      if (response.error) {
        toast({
          title: 'Error',
          description: response.error,
          variant: 'destructive'
        });
        return;
      }

      if (response.data) {
        toast({
          title: 'Success',
          description: 'Matter created successfully',
        });
        router.push(`/matters/${response.data.id}`);
      }
    } catch (error) {
      console.error('Failed to create matter:', error);
      toast({
        title: 'Error',
        description: 'Failed to create matter. Please try again.',
        variant: 'destructive'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-cream-50 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-brown-700" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-cream-50 flex items-center justify-center">
        <Card className="w-96">
          <CardHeader>
            <CardTitle className="text-center">Authentication Required</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-center text-muted-foreground">
              Please sign in to create a new matter.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-cream-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link href="/dashboard">
            <Button variant="ghost" className="mb-4 text-brown-600 hover:text-brown-800">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
          </Link>
          <h1 className="text-3xl font-bold text-brown-900 mb-2">Create New Matter</h1>
          <p className="text-brown-600">
            Set up a new legal research project to organize your documents and analysis.
          </p>
        </div>

        {/* Main Form */}
        <Card className="bg-white border-stone-200">
          <CardHeader>
            <CardTitle className="text-xl  text-brown-900">Matter Details</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Title Field */}
              <div className="space-y-2">
                <Label htmlFor="title" className="text-sm font-medium text-brown-700">
                  Matter Title *
                </Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  placeholder="e.g., Contract Dispute Analysis - ABC Corp vs XYZ Ltd"
                  className={`${errors.title ? 'border-red-500 focus:border-red-500' : 'border-stone-300 focus:border-brown-500'}`}
                  disabled={isLoading}
                />
                {errors.title && (
                  <p className="text-sm text-red-600 flex items-center gap-1">
                    <AlertCircle className="h-4 w-4" />
                    {errors.title}
                  </p>
                )}
                <p className="text-xs text-brown-500">
                  Choose a descriptive title that will help you identify this matter later.
                </p>
              </div>

              {/* Language Field */}
              <div className="space-y-2">
                <Label htmlFor="language" className="text-sm font-medium text-brown-700">
                  Primary Language
                </Label>
                <Select
                  value={formData.language}
                  onValueChange={(value: 'en' | 'hi') => handleInputChange('language', value)}
                  disabled={isLoading}
                >
                  <SelectTrigger className="border-stone-300 focus:border-brown-500">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="hi">Hindi (हिन्दी)</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-brown-500">
                  This will be the primary language for document processing and analysis.
                </p>
              </div>

              {/* Description Field */}
              <div className="space-y-2">
                <Label htmlFor="description" className="text-sm font-medium text-brown-700">
                  Description (Optional)
                </Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="Brief description of the matter, key issues, or important context..."
                  className="border-stone-300 focus:border-brown-500 min-h-[100px] resize-none"
                  disabled={isLoading}
                />
                <p className="text-xs text-brown-500">
                  Add any relevant context or notes about this matter.
                </p>
              </div>

              {/* Submit Buttons */}
              <div className="flex items-center justify-between pt-6 border-t border-stone-200">
                <Link href="/dashboard">
                  <Button variant="outline" disabled={isLoading} className="border-stone-300 text-brown-700">
                    Cancel
                  </Button>
                </Link>
                <Button
                  type="submit"
                  disabled={isLoading || !formData.title.trim()}
                  className="bg-brown-700 hover:bg-brown-600 text-cream-100"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    <>
                      <Plus className="h-4 w-4 mr-2" />
                      Create Matter
                    </>
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Help Card */}
        <Card className="mt-6 bg-blue-50 border-blue-200">
          <CardContent className="p-6">
            <h3 className="font-semibold text-blue-900 mb-2">Getting Started Tips</h3>
            <ul className="space-y-1 text-sm text-blue-800">
              <li>• Use descriptive titles to easily identify your matters</li>
              <li>• You can upload documents in PDF, DOCX, or image formats</li>
              <li>• The AI will automatically process and index your documents</li>
              <li>• All research queries and results are securely stored</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
