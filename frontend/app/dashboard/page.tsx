'use client';

import { useEffect, useState } from 'react';
import { useUser } from '@clerk/nextjs';
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { DashboardStats } from "@/components/dashboard/DashboardStats";
import { MattersGrid } from "@/components/dashboard/MattersGrid";
import { RecentActivity } from "@/components/dashboard/RecentActivity";
import { QuickActions } from "@/components/dashboard/QuickActions";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, Loader2 } from "lucide-react";
import { apiClient } from "@/lib/api";
import type { Matter, Analytics } from "@/types";

export default function Dashboard() {
  const { user, isLoaded } = useUser();
  const [matters, setMatters] = useState<Matter[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [isLoadingMatters, setIsLoadingMatters] = useState(true);
  const [isLoadingAnalytics, setIsLoadingAnalytics] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isLoaded && user) {
      loadDashboardData();
    }
  }, [isLoaded, user]);

  const loadDashboardData = async () => {
    try {
      // Load matters
      const mattersResponse = await apiClient.getMatters();
      if (mattersResponse.error) {
        setError(mattersResponse.error);
      } else if (mattersResponse.data) {
        setMatters(mattersResponse.data);
      }
      setIsLoadingMatters(false);

      // Load analytics
      const analyticsResponse = await apiClient.getAnalytics();
      if (analyticsResponse.error) {
        console.warn('Failed to load analytics:', analyticsResponse.error);
      } else if (analyticsResponse.data) {
        setAnalytics(analyticsResponse.data);
      }
      setIsLoadingAnalytics(false);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError('Failed to load dashboard data');
      setIsLoadingMatters(false);
      setIsLoadingAnalytics(false);
    }
  };

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-cream-50">
        <div className="flex items-center justify-center min-h-screen">
          <Loader2 className="h-8 w-8 animate-spin text-brown-700" />
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-cream-50">
        <div className="flex items-center justify-center min-h-screen">
          <Card className="w-96">
            <CardHeader>
              <CardTitle className="text-center">Authentication Required</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-center text-muted-foreground">
                Please sign in to access your dashboard.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-cream-50">
      <DashboardHeader />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Welcome Section */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-brown-900 mb-2">
              Welcome back, {user.firstName || user.emailAddresses[0]?.emailAddress}
            </h1>
            <p className="text-brown-600">
              Your legal research workspace is ready. Start by creating a new matter or continue with existing ones.
            </p>
          </div>

          {/* Error Alert */}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Quick Actions */}
          <QuickActions />

          {/* Analytics Stats */}
          {isLoadingAnalytics ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[...Array(4)].map((_, i) => (
                <Card key={i}>
                  <CardHeader className="pb-2">
                    <Skeleton className="h-4 w-24" />
                  </CardHeader>
                  <CardContent>
                    <Skeleton className="h-8 w-16 mb-2" />
                    <Skeleton className="h-3 w-32" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <DashboardStats analytics={analytics} />
          )}

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Matters Grid */}
            <div className="lg:col-span-2">
              {isLoadingMatters ? (
                <Card>
                  <CardHeader>
                    <CardTitle>Your Matters</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {[...Array(3)].map((_, i) => (
                        <div key={i} className="flex items-center space-x-4">
                          <Skeleton className="h-12 w-12" />
                          <div className="space-y-2 flex-1">
                            <Skeleton className="h-4 w-full" />
                            <Skeleton className="h-3 w-2/3" />
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <MattersGrid matters={matters} onRefresh={loadDashboardData} />
              )}
            </div>

            {/* Recent Activity */}
            <div className="space-y-6">
              <RecentActivity activities={analytics?.recent_activity || []} />
              
              {/* Quick Stats Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Quick Stats</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Total Matters</span>
                    <span className="font-semibold">{matters.length}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Documents Processed</span>
                    <span className="font-semibold">{analytics?.total_documents || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Queries Made</span>
                    <span className="font-semibold">{analytics?.total_queries || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Avg. Confidence</span>
                    <span className="font-semibold">
                      {analytics?.avg_confidence ? `${(analytics.avg_confidence * 100).toFixed(1)}%` : 'N/A'}
                    </span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
