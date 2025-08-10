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
    title: "Create New Matter",
    description: "Start a new legal research project",
    icon: Plus,
    href: "/matters/new",
    bgColor: "#000",
    hoverBg: "#000",
  },
  {
    title: "Search Precedents",
    description: "Quick search across legal database",
    icon: Search,
    href: "/search",
    bgColor: "#000",
    hoverBg: "#000",
  },
  {
    title: "View Knowledge Base",
    description: "Browse legal resources and guides",
    icon: BookOpen,
    href: "/knowledge",
    bgColor: "#000",
    hoverBg: "#000",
  },
];

export function QuickActions() {
  return (
    <Card style={{ backgroundColor: 'white', borderColor: '#D1D5DB' }}>
      <CardHeader>
        <CardTitle className="text-xl" >Quick Actions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <Link key={action.title} href={action.href}>
                <Button
                  variant="outline"
                  className="w-full h-auto p-4 flex flex-col items-center space-y-2 hover:scale-105 hover:shadow-md transition-all text-white"
                  style={{
                    backgroundColor: action.bgColor,
                    borderColor: action.bgColor,
                    color: 'white'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = action.hoverBg}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = action.bgColor}
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
