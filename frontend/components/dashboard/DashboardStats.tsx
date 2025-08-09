import { Card, CardContent } from '@/components/ui/card';
import { FileText, MessageSquare, TrendingUp, CreditCard } from 'lucide-react';
import type { Analytics } from '@/types';

interface DashboardStatsProps {
  analytics: Analytics | null;
}

export function DashboardStats({ analytics }: DashboardStatsProps) {
  const stats = [
    {
      icon: FileText,
      label: 'Documents Processed',
      value: analytics?.total_documents?.toString() || '0',
      change: 'Across all matters',
      changeType: 'neutral' as const
    },
    {
      icon: MessageSquare,
      label: 'Research Queries',
      value: analytics?.total_queries?.toString() || '0',
      change: 'Legal research made',
      changeType: 'positive' as const
    },
    {
      icon: TrendingUp,
      label: 'Avg. Confidence',
      value: analytics?.avg_confidence 
        ? `${(analytics.avg_confidence * 100).toFixed(1)}%`
        : 'N/A',
      change: 'Research accuracy',
      changeType: 'positive' as const
    },
    {
      icon: CreditCard,
      label: 'Credits Used',
      value: analytics?.credits_used?.toString() || '0',
      change: 'This month',
      changeType: 'neutral' as const
    }
  ];
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <Card key={index} className="bg-cream-100 border-stone-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-brown-500 mb-1">{stat.label}</p>
                  <p className="text-2xl font-display font-bold text-brown-900">{stat.value}</p>
                  <p className={`text-xs ${
                    stat.changeType === 'positive' ? 'text-olive-400' : 'text-brown-500'
                  }`}>
                    {stat.change}
                  </p>
                </div>
                <div className="p-3 bg-brown-700 text-cream-100 rounded-md">
                  <Icon className="h-5 w-5" />
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}