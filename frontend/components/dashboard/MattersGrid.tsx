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
      return { backgroundColor: '#22C55E', color: 'white' };
    case 'completed':
      return { backgroundColor: '#3B82F6', color: 'white' };
    case 'processing':
      return { backgroundColor: '#F59E0B', color: 'white' };
    case 'archived':
      return { backgroundColor: '#6B7280', color: 'white' };
    default:
      return { backgroundColor: '#E5E7EB', color: '#374151' };
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
        <h2 className="text-2xl  font-bold" style={{ color: 'orangered' }}>Your Matters</h2>
        <Link href="/matters/new">
          <Button
            variant="outline"
            className="hover:bg-gray-50"
            style={{ borderColor: 'orangered', color: 'orangered' }}
          >
            Create New Matter
          </Button>
        </Link>
      </div>

      {matters.length === 0 ? (
        <Card style={{ backgroundColor: 'white', borderColor: '#D1D5DB' }} className="text-center py-12">
          <CardContent>
            <FileText className="h-12 w-12 mx-auto mb-4" style={{ color: '#9CA3AF' }} />
            <h3 className="text-lg font-semibold mb-2" style={{ color: 'orangered' }}>No matters yet</h3>
            <p className="mb-6" style={{ color: '#6B7280' }}>
              Create your first matter to start your legal research journey
            </p>
            <Link href="/matters/new">
              <Button
                className="text-white hover:opacity-90"
                style={{ backgroundColor: 'orangered' }}
              >
                <Plus className="h-4 w-4 mr-2" />
                Create Your First Matter
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {matters.map((matter) => (
            <Card
              key={matter.id}
              className="hover:shadow-lg transition-all"
              style={{ backgroundColor: 'white', borderColor: '#D1D5DB' }}
            >
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="text-lg  font-semibold mb-2" style={{ color: 'orangered' }}>
                      {matter.title}
                    </h3>
                    <div className="flex items-center gap-2 mb-2">
                      <Badge
                        variant="secondary"
                        style={getStatusColor(matter.status || 'active')}
                      >
                        {matter.status || 'active'}
                      </Badge>
                      <Badge
                        variant="outline"
                        style={{ borderColor: 'orangered', color: 'orangered' }}
                      >
                        {matter.language === 'hi' ? 'Hindi' : 'English'}
                      </Badge>
                    </div>
                  </div>
                  <Button variant="ghost" size="icon" className="hover:bg-gray-100" style={{ color: '#6B7280' }}>
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="flex items-center justify-between text-sm mb-4" style={{ color: '#6B7280' }}>
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
                  <Button
                    className="w-full text-white hover:opacity-90"
                    style={{ backgroundColor: 'orangered' }}
                  >
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
