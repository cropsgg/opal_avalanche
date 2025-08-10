'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  FileText, 
  MessageSquare, 
  Download, 
  Shield,
  Clock,
  ArrowRight
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import type { Activity } from '@/types';

interface RecentActivityProps {
  activities: Activity[];
}

const getActivityIcon = (type: string) => {
  switch (type) {
    case 'query':
      return MessageSquare;
    case 'upload':
      return FileText;
    case 'export':
      return Download;
    case 'notarization':
      return Shield;
    default:
      return Clock;
  }
};

const getActivityColor = (type: string) => {
  switch (type) {
    case 'query':
      return { backgroundColor: '#DBEAFE', color: '#1D4ED8' };
    case 'upload':
      return { backgroundColor: '#D1FAE5', color: '#059669' };
    case 'export':
      return { backgroundColor: '#E9D5FF', color: '#7C3AED' };
    case 'notarization':
      return { backgroundColor: '#FED7AA', color: 'orangered' };
    default:
      return { backgroundColor: '#F3F4F6', color: '#374151' };
  }
};

const formatActivityTime = (timestamp: string) => {
  try {
    return formatDistanceToNow(new Date(timestamp), { addSuffix: true });
  } catch {
    return 'Recently';
  }
};

export function RecentActivity({ activities }: RecentActivityProps) {
  if (activities.length === 0) {
    return (
      <Card style={{ backgroundColor: 'white', borderColor: '#D1D5DB' }}>
        <CardHeader>
          <CardTitle className="text-lg font-display" style={{ color: 'orangered' }}>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Clock className="h-12 w-12 mx-auto mb-4" style={{ color: '#9CA3AF' }} />
            <p style={{ color: '#6B7280' }}>No recent activity</p>
            <p className="text-sm" style={{ color: '#9CA3AF' }}>Your activity will appear here</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card style={{ backgroundColor: 'white', borderColor: '#D1D5DB' }}>
      <CardHeader>
        <CardTitle className="text-lg font-display" style={{ color: 'orangered' }}>Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.slice(0, 5).map((activity, index) => {
            const Icon = getActivityIcon(activity.type);
            return (
              <div key={index} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
                <div 
                  className="p-2 rounded-full"
                  style={getActivityColor(activity.type)}
                >
                  <Icon className="h-4 w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium" style={{ color: '#111827' }}>
                    {activity.description}
                  </p>
                  <div className="flex items-center mt-1 space-x-2">
                    <p className="text-xs" style={{ color: '#6B7280' }}>
                      {formatActivityTime(activity.timestamp)}
                    </p>
                    <Badge 
                      variant="outline" 
                      className="text-xs"
                      style={{ borderColor: '#D1D5DB', color: '#6B7280' }}
                    >
                      {activity.type}
                    </Badge>
                  </div>
                </div>
                <ArrowRight className="h-4 w-4 flex-shrink-0" style={{ color: '#9CA3AF' }} />
              </div>
            );
          })}
          
          {activities.length > 5 && (
            <div className="text-center pt-4" style={{ borderTop: '1px solid #E5E7EB' }}>
              <button 
                className="text-sm font-medium hover:opacity-80 transition-opacity"
                style={{ color: 'orangered' }}
              >
                View All Activity
              </button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
