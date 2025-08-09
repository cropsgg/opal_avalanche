import { Card, CardContent } from '@/components/ui/card';
import { FileText, Clock, CheckCircle, AlertCircle } from 'lucide-react';

const stats = [
  {
    icon: FileText,
    label: 'Active Matters',
    value: '12',
    change: '+3 this month',
    changeType: 'positive' as const
  },
  {
    icon: Clock,
    label: 'Hours Saved',
    value: '147',
    change: 'This quarter',
    changeType: 'neutral' as const
  },
  {
    icon: CheckCircle,
    label: 'Verified Citations',
    value: '1,234',
    change: '100% accuracy',
    changeType: 'positive' as const
  },
  {
    icon: AlertCircle,
    label: 'Credits Used',
    value: '67/100',
    change: 'Resets in 12 days',
    changeType: 'neutral' as const
  }
];

export function DashboardStats() {
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