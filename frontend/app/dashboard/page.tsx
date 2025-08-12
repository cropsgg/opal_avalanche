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

// --- Dummy sexy matters ---
const now = Date.now();
const days = (n: number) =>
  new Date(now - n * 24 * 60 * 60 * 1000).toISOString();
const DUMMY_MATTERS: Matter[] = [
  {
    id: "mat_prop_limitation_delhi",
    user_id: "u_demo",
    title: "Property Dispute – Limitation (Delhi HC)",
    language: "en",
    created_at: days(2),
    documents_count: 12,
    last_analysis:
      "DAO verdict: proceed with suit · confidence 77.3% · Sec 17(1)(b) Limitation Act",
    status: "active",
  },
  {
    id: "mat_contract_damages",
    user_id: "u_demo",
    title: "Contract Breach – Damages Memo",
    language: "en",
    created_at: days(6),
    documents_count: 5,
    last_analysis:
      "Drafted statement of claim · identified key precedents on mitigation",
    status: "draft",
  },
  {
    id: "mat_trademark_reply",
    user_id: "u_demo",
    title: "Trademark Opposition – Reply Draft",
    language: "en",
    created_at: days(15),
    documents_count: 8,
    last_analysis:
      "Pulled persuasive authorities from Bombay HC · high similarity",
    status: "active",
  },
  {
    id: "mat_condonation_civil_appeal",
    user_id: "u_demo",
    title: "Civil Appeal – Condonation Application",
    language: "en",
    created_at: days(28),
    documents_count: 3,
    last_analysis: "Computed delay timeline · prepared affidavit grounds",
    status: "archived",
  },
  {
    id: "mat_ni138_cheque",
    user_id: "u_demo",
    title: "Cheque Bounce – Sec 138 NI Act",
    language: "hi",
    created_at: days(9),
    documents_count: 4,
    last_analysis: "Compiled notices & bank memos · precedent scan complete",
    status: "active",
  },
  {
    id: "mat_lease_eviction",
    user_id: "u_demo",
    title: "Lease Dispute – Eviction Petition",
    language: "en",
    created_at: days(4),
    documents_count: 6,
    last_analysis: "Drafted petition skeleton · gathered rent ledger evidence",
    status: "draft",
  },
];

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
      // Load matters (dummy for now)
      setMatters(DUMMY_MATTERS);

      setIsLoadingMatters(false);

      // Load analytics
      const analyticsResponse = await apiClient.getAnalytics();
      if (analyticsResponse.error) {
        console.warn("Failed to load analytics:", analyticsResponse.error);
        // Seed dummy analytics if backend not ready
        setAnalytics({
          total_queries: 42,
          total_documents: DUMMY_MATTERS.reduce(
            (a, m) => a + (m.documents_count || 0),
            0
          ),
          avg_confidence: 0.912,
          credits_used: 73,
          recent_activity: [],
        } as Analytics);
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
      <div
        className={`!${poppins.className} min-h-screen`}
        style={{ backgroundColor: "#EFEAE3" }}
      >
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
    <div
      className={`${poppins.className} min-h-screen`}
      style={{ backgroundColor: "#EFEAE3" }}
    >
      <DashboardHeader />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Welcome Section */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2">
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
                    <CardTitle className="font-poppins !text-[#000]">
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
                  <CardTitle className="text-lg text-[#000]">
                    Quick Stats
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">
                      Total Matters
                    </span>
                    <span className="font-semibold" style={{ color: "#000" }}>
                      {matters.length}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">
                      Documents Processed
                    </span>
                    <span className="font-semibold" style={{ color: "#000" }}>
                      {analytics?.total_documents ||
                        DUMMY_MATTERS.reduce(
                          (a, m) => a + (m.documents_count || 0),
                          0
                        )}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">
                      Queries Made
                    </span>
                    <span className="font-semibold" style={{ color: "#000" }}>
                      {analytics?.total_queries || 42}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">
                      Avg. Confidence
                    </span>
                    <span className="font-semibold" style={{ color: "#000" }}>
                      {analytics?.avg_confidence
                        ? `${(analytics.avg_confidence * 100).toFixed(1)}%`
                        : "91.2%"}
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
