import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Calendar, ExternalLink, FileText, Gavel, Scale, BookOpen } from "lucide-react";

interface SearchResult {
  id: string;
  title: string;
  description: string;
  type: 'case' | 'statute' | 'document' | 'precedent';
  date?: string;
  source?: string;
  relevance_score?: number;
  url?: string;
  excerpt?: string;
}

interface SearchResultCardProps {
  result: SearchResult;
  onClick?: () => void;
}

export function SearchResultCard({ result, onClick }: SearchResultCardProps) {
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'case': return <Gavel className="h-4 w-4" />;
      case 'statute': return <Scale className="h-4 w-4" />;
      case 'document': return <FileText className="h-4 w-4" />;
      case 'precedent': return <BookOpen className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'case': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'statute': return 'bg-green-100 text-green-800 border-green-200';
      case 'document': return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'precedent': return 'bg-orange-100 text-orange-800 border-orange-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return null;
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <Card
      className="hover:shadow-lg transition-shadow cursor-pointer"
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg text-brown-900 mb-2 flex items-center gap-2">
              {getTypeIcon(result.type)}
              {result.title}
            </CardTitle>
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <Badge
                variant="outline"
                className={getTypeColor(result.type)}
              >
                {result.type.charAt(0).toUpperCase() + result.type.slice(1)}
              </Badge>
              {result.date && (
                <div className="flex items-center text-sm text-brown-600">
                  <Calendar className="h-3 w-3 mr-1" />
                  {formatDate(result.date)}
                </div>
              )}
              {result.relevance_score && (
                <Badge variant="secondary" className="text-xs">
                  {Math.round(result.relevance_score * 100)}% match
                </Badge>
              )}
            </div>
          </div>
          {result.url && (
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                window.open(result.url, '_blank');
              }}
              className="flex-shrink-0"
            >
              <ExternalLink className="h-4 w-4" />
            </Button>
          )}
        </div>
        {result.description && (
          <CardDescription className="text-brown-600 line-clamp-2">
            {result.description}
          </CardDescription>
        )}
      </CardHeader>
      {result.excerpt && (
        <CardContent className="pt-0">
          <div className="bg-stone-50 rounded-md p-3 border-l-4 border-brown-200">
            <p className="text-sm text-brown-800 italic line-clamp-3">
              "{result.excerpt}"
            </p>
          </div>
          {result.source && (
            <p className="text-xs text-brown-500 mt-2 truncate">
              Source: {result.source}
            </p>
          )}
        </CardContent>
      )}
    </Card>
  );
}
