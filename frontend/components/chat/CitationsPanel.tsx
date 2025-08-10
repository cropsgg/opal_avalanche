"use client";

import { Citation } from "@/app/chat/page";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ExternalLink, FileText } from "lucide-react";
import { cn } from "@/lib/utils";

interface CitationsPanelProps {
  citations: Citation[];
}

export function CitationsPanel({ citations }: CitationsPanelProps) {
  const sortedCitations = citations.sort((a, b) => b.relevanceScore - a.relevanceScore);

  return (
    <div className="h-full bg-gray-50 border-l border-gray-200">
      <div className="p-4 border-b border-gray-200 bg-white">
        <h2 className="text-lg font-semibold text-black flex items-center">
          <FileText className="w-5 h-5 mr-2" />
          Citations
        </h2>
        {citations.length > 0 && (
          <p className="text-sm text-gray-600 mt-1">
            {citations.length} relevant sources found
          </p>
        )}
      </div>

      <div className="overflow-y-auto h-[calc(100%-80px)] p-4">
        {citations.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Citations will appear here when you ask a question</p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {sortedCitations.map((citation) => (
              <CitationCard key={citation.id} citation={citation} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function CitationCard({ citation }: { citation: Citation }) {
  const relevanceColor =
    citation.relevanceScore >= 0.8 ? "bg-green-100 text-green-800" :
    citation.relevanceScore >= 0.6 ? "bg-yellow-100 text-yellow-800" :
    "bg-red-100 text-red-800";

  const relevanceLabel =
    citation.relevanceScore >= 0.8 ? "High" :
    citation.relevanceScore >= 0.6 ? "Medium" : "Low";

  return (
    <Card className="bg-white border-gray-200 hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <CardTitle className="text-sm font-medium text-black leading-tight">
            {citation.title}
          </CardTitle>
          {citation.url && (
            <a
              href={citation.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-gray-600 flex-shrink-0 ml-2"
            >
              <ExternalLink className="w-4 h-4" />
            </a>
          )}
        </div>

        <div className="flex items-center space-x-2">
          <Badge className={cn("text-xs", relevanceColor)}>
            {relevanceLabel} Relevance
          </Badge>
          <span className="text-xs text-gray-500">
            {Math.round(citation.relevanceScore * 100)}%
          </span>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <div className="space-y-2">
          <p className="text-xs text-gray-600 font-medium">
            Source: {citation.source}
          </p>

          <blockquote className="text-sm text-gray-700 italic border-l-2 border-gray-300 pl-3">
            "{citation.excerpt}"
          </blockquote>
        </div>
      </CardContent>
    </Card>
  );
}
