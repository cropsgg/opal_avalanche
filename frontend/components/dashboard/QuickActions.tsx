'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Plus, 
  Upload, 
  Search, 
  BookOpen,
  MessageSquare,
  FileText 
} from 'lucide-react';
import Link from 'next/link';

const quickActions = [
  {
    title: 'Create New Matter',
    description: 'Start a new legal research project',
    icon: Plus,
    href: '/matters/new',
    color: 'bg-brown-700 hover:bg-brown-600 text-cream-100'
  },
  {
    title: 'Upload Documents',
    description: 'Add documents to existing matter',
    icon: Upload,
    href: '/dashboard#upload',
    color: 'bg-olive-600 hover:bg-olive-500 text-cream-100'
  },
  {
    title: 'Search Precedents',
    description: 'Quick search across legal database',
    icon: Search,
    href: '/search',
    color: 'bg-gold-600 hover:bg-gold-500 text-brown-900'
  },
  {
    title: 'View Knowledge Base',
    description: 'Browse legal resources and guides',
    icon: BookOpen,
    href: '/knowledge',
    color: 'bg-stone-600 hover:bg-stone-500 text-cream-100'
  }
];

export function QuickActions() {
  return (
    <Card className="bg-white border-stone-200">
      <CardHeader>
        <CardTitle className="text-xl font-display text-brown-900">Quick Actions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <Link key={action.title} href={action.href}>
                <Button 
                  variant="outline" 
                  className={`w-full h-auto p-4 flex flex-col items-center space-y-2 border-stone-200 hover:shadow-md transition-all ${action.color}`}
                >
                  <Icon className="h-6 w-6" />
                  <div className="text-center">
                    <div className="font-semibold text-sm">{action.title}</div>
                    <div className="text-xs opacity-80">{action.description}</div>
                  </div>
                </Button>
              </Link>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
