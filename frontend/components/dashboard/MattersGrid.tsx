'use client';

import Link from 'next/link';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { FileText, MessageSquare, Clock, MoreVertical, Plus } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import type { Matter } from '@/types';

interface MattersGridProps {
  matters: Matter[];
  onRefresh: () => void;
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'active':
      return 'bg-olive-400 text-cream-100';
    case 'completed':
      return 'bg-brown-500 text-cream-100';
    case 'processing':
      return 'bg-gold-500 text-brown-900';
    case 'archived':
      return 'bg-stone-400 text-cream-100';
    default:
      return 'bg-stone-200 text-brown-700';
  }
};

const formatLastActivity = (dateString: string) => {
  try {
    return formatDistanceToNow(new Date(dateString), { addSuffix: true });
  } catch {
    return 'Recently';
  }
};

export function MattersGrid({ matters, onRefresh }: MattersGridProps) {
  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-display font-bold text-brown-900">Your Matters</h2>
        <Link href="/matters/new">
          <Button variant="outline" className="border-brown-700 text-brown-700 hover:bg-brown-50">
            Create New Matter
          </Button>
        </Link>
      </div>

      {matters.length === 0 ? (
        <Card className="bg-cream-100 border-stone-200 text-center py-12">
          <CardContent>
            <FileText className="h-12 w-12 text-brown-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-brown-900 mb-2">No matters yet</h3>
            <p className="text-brown-500 mb-6">
              Create your first matter to start your legal research journey
            </p>
            <Link href="/matters/new">
              <Button className="bg-brown-700 hover:bg-brown-500 text-cream-100">
                <Plus className="h-4 w-4 mr-2" />
                Create Your First Matter
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {matters.map((matter) => (
            <Card key={matter.id} className="bg-cream-100 border-stone-200 hover:shadow-lg transition-all hover:bg-white">
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="text-lg font-display font-semibold text-brown-900 mb-2">
                      {matter.title}
                    </h3>
                    <div className="flex items-center gap-2 mb-2">
                      <Badge className={getStatusColor(matter.status || 'active')} variant="secondary">
                        {matter.status || 'active'}
                      </Badge>
                      <Badge variant="outline" className="border-brown-500 text-brown-700">
                        {matter.language === 'hi' ? 'Hindi' : 'English'}
                      </Badge>
                    </div>
                  </div>
                  <Button variant="ghost" size="icon" className="text-brown-500 hover:text-brown-700">
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="flex items-center justify-between text-sm text-brown-500 mb-4">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1">
                      <FileText className="h-4 w-4" />
                      <span>{matter.documents_count || 0} docs</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="h-4 w-4" />
                    <span>{formatLastActivity(matter.created_at)}</span>
                  </div>
                </div>
                <Link href={`/matters/${matter.id}`}>
                  <Button className="w-full bg-brown-700 hover:bg-brown-500 text-cream-100">
                    Open Matter
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}