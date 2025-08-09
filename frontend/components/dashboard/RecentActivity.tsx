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
      return 'bg-blue-100 text-blue-700';
    case 'upload':
      return 'bg-green-100 text-green-700';
    case 'export':
      return 'bg-purple-100 text-purple-700';
    case 'notarization':
      return 'bg-orange-100 text-orange-700';
    default:
      return 'bg-gray-100 text-gray-700';
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
      <Card className="bg-white border-stone-200">
        <CardHeader>
          <CardTitle className="text-lg font-display text-brown-900">Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Clock className="h-12 w-12 text-brown-400 mx-auto mb-4" />
            <p className="text-brown-500">No recent activity</p>
            <p className="text-sm text-brown-400">Your activity will appear here</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-white border-stone-200">
      <CardHeader>
        <CardTitle className="text-lg font-display text-brown-900">Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.slice(0, 5).map((activity, index) => {
            const Icon = getActivityIcon(activity.type);
            return (
              <div key={index} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-stone-50 transition-colors">
                <div className={`p-2 rounded-full ${getActivityColor(activity.type)}`}>
                  <Icon className="h-4 w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-brown-900">
                    {activity.description}
                  </p>
                  <div className="flex items-center mt-1 space-x-2">
                    <p className="text-xs text-brown-500">
                      {formatActivityTime(activity.timestamp)}
                    </p>
                    <Badge variant="outline" className="text-xs">
                      {activity.type}
                    </Badge>
                  </div>
                </div>
                <ArrowRight className="h-4 w-4 text-brown-400 flex-shrink-0" />
              </div>
            );
          })}
          
          {activities.length > 5 && (
            <div className="text-center pt-4 border-t border-stone-200">
              <button className="text-sm text-brown-600 hover:text-brown-800 font-medium">
                View All Activity
              </button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
