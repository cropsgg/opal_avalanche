'use client';

import Link from 'next/link';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { FileText, MessageSquare, Clock, MoreVertical } from 'lucide-react';

// Mock data for demonstration
const matters = [
  {
    id: '1',
    title: 'Contract Dispute Analysis',
    status: 'active',
    language: 'English',
    lastActivity: '2 hours ago',
    documentsCount: 12,
    messagesCount: 8,
    description: 'Commercial contract breach analysis with damages assessment'
  },
  {
    id: '2', 
    title: 'Property Rights Research',
    status: 'completed',
    language: 'Hindi',
    lastActivity: '1 day ago',
    documentsCount: 6,
    messagesCount: 15,
    description: 'Land acquisition rights and compensation analysis'
  },
  {
    id: '3',
    title: 'Corporate Compliance Review',
    status: 'processing',
    language: 'English',
    lastActivity: '3 hours ago',
    documentsCount: 24,
    messagesCount: 3,
    description: 'Securities law compliance and regulatory requirements'
  },
  {
    id: '4',
    title: 'Criminal Appeal Brief',
    status: 'active',
    language: 'English',
    lastActivity: '5 hours ago',
    documentsCount: 8,
    messagesCount: 12,
    description: 'High Court criminal appeal with precedent analysis'
  }
];

const getStatusColor = (status: string) => {
  switch (status) {
    case 'active':
      return 'bg-olive-400 text-cream-100';
    case 'completed':
      return 'bg-brown-500 text-cream-100';
    case 'processing':
      return 'bg-gold-500 text-brown-900';
    default:
      return 'bg-stone-200 text-brown-700';
  }
};

export function MattersGrid() {
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
                    <Badge className={getStatusColor(matter.status)} variant="secondary">
                      {matter.status}
                    </Badge>
                    <Badge variant="outline" className="border-brown-500 text-brown-700">
                      {matter.language}
                    </Badge>
                  </div>
                </div>
                <Button variant="ghost" size="icon" className="text-brown-500 hover:text-brown-700">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </div>
              <p className="text-brown-500 text-sm leading-relaxed">
                {matter.description}
              </p>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="flex items-center justify-between text-sm text-brown-500 mb-4">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-1">
                    <FileText className="h-4 w-4" />
                    <span>{matter.documentsCount} docs</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <MessageSquare className="h-4 w-4" />
                    <span>{matter.messagesCount}</span>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  <span>{matter.lastActivity}</span>
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
    </div>
  );
}