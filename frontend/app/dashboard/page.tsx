"use client";

import { useEffect, useState } from "react";
import { useUser } from "@clerk/nextjs";
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
import { Inter, Poppins } from "next/font/google";
const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-poppins",
});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});
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

      setIsLoadingMatters(false);

      // Load analytics
      const analyticsResponse = await apiClient.getAnalytics();
      if (analyticsResponse.error) {
        console.warn("Failed to load analytics:", analyticsResponse.error);
      } else if (analyticsResponse.data) {
        setAnalytics(analyticsResponse.data);
      }
      setIsLoadingAnalytics(false);
    } catch (err) {
      console.error("Failed to load dashboard data:", err);
      setError("Failed to load dashboard data");
      setIsLoadingMatters(false);
      setIsLoadingAnalytics(false);
    }
  };

  if (!isLoaded) {
    return (
      <div className="min-h-screen" style={{ backgroundColor: "#EFEAE3" }}>
        <div className="flex items-center justify-center min-h-screen">
          <Loader2
            className="h-8 w-8 animate-spin"
            style={{ color: "orangered" }}
          />
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className={`!${poppins.className} min-h-screen`} style={{ backgroundColor: "#EFEAE3" }}>
        <div className="flex items-center justify-center min-h-screen">
          <Card
            className="w-96"
            style={{ backgroundColor: "white", borderColor: "orangered" }}
          >
            <CardHeader>
              <CardTitle className="text-center" style={{ color: "orangered" }}>
                Authentication Required
              </CardTitle>
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
    <div className={`${poppins.className} min-h-screen`} style={{ backgroundColor: "#EFEAE3" }}>
      <DashboardHeader />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Welcome Section */}
          <div className="mb-8">
            <h1
              className="text-3xl font-bold mb-2"
            >
              Welcome back,{" "}
              {user.firstName || user.emailAddresses[0]?.emailAddress}
            </h1>
            <p className="text-gray-700">
              Your legal research workspace is ready. Start by creating a new
              matter or continue with existing ones.
            </p>
          </div>

          {/* Error Alert */}
          {error && (
            <Alert
              variant="destructive"
              style={{ borderColor: "orangered", backgroundColor: "#FFF5F5" }}
            >
              <AlertCircle className="h-4 w-4" style={{ color: "orangered" }} />
              <AlertDescription style={{ color: "orangered" }}>
                {error}
              </AlertDescription>
            </Alert>
          )}

          {/* Quick Actions */}
          <QuickActions />

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Matters Grid */}
            <div className="lg:col-span-2">
              {isLoadingMatters ? (
                <Card
                  style={{ backgroundColor: "white", borderColor: "#E5E7EB" }}
                >
                  <CardHeader>
                    <CardTitle  className="font-poppins text-black">
                      Your Matters
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {[...Array(3)].map((_, i) => (
                        <div key={i} className="flex items-center space-x-4">
                          <Skeleton
                            className="h-12 w-12"
                            style={{ backgroundColor: "#F3F4F6" }}
                          />
                          <div className="space-y-2 flex-1">
                            <Skeleton
                              className="h-4 w-full"
                              style={{ backgroundColor: "#F3F4F6" }}
                            />
                            <Skeleton
                              className="h-3 w-2/3"
                              style={{ backgroundColor: "#F3F4F6" }}
                            />
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
              {/* Quick Stats Card */}
              <Card
                style={{ backgroundColor: "white", borderColor: "#E5E7EB" }}
              >
                <CardHeader>
                  <CardTitle className="text-lg" style={{ color: "orangered" }}>
                    Quick Stats
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">
                      Total Matters
                    </span>
                    <span
                      className="font-semibold"
                      style={{ color: "orangered" }}
                    >
                      {matters.length}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">
                      Documents Processed
                    </span>
                    <span
                      className="font-semibold"
                      style={{ color: "orangered" }}
                    >
                      {analytics?.total_documents || 0}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">
                      Queries Made
                    </span>
                    <span
                      className="font-semibold"
                      style={{ color: "orangered" }}
                    >
                      {analytics?.total_queries || 0}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">
                      Avg. Confidence
                    </span>
                    <span
                      className="font-semibold"
                      style={{ color: "orangered" }}
                    >
                      {analytics?.avg_confidence
                        ? `${(analytics.avg_confidence * 100).toFixed(1)}%`
                        : "N/A"}
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
