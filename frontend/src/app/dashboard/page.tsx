"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Briefcase, 
  Target, 
  TrendingUp, 
  Users, 
  Play, 
  Pause, 
  Settings,
  Plus,
  Search,
  Heart,
  CheckCircle
} from "lucide-react";

interface DashboardStats {
  total_applications: number;
  successful_applications: number;
  failed_applications: number;
  pending_applications: number;
  active_sessions: number;
  total_sessions: number;
  active_rules: number;
  total_saved_jobs: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<any>(null);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    const userData = localStorage.getItem("user");
    
    if (!token) {
      router.push("/auth/login");
      return;
    }
    
    if (userData) {
      setUser(JSON.parse(userData));
    }

    fetchDashboardStats(token);
  }, [router]);

  const fetchDashboardStats = async (token: string) => {
    try {
      const [automationResponse, jobResponse] = await Promise.all([
        fetch("http://localhost:8000/api/automation/stats/", {
          headers: { Authorization: `Token ${token}` },
        }),
        fetch("http://localhost:8000/api/jobs/analytics/", {
          headers: { Authorization: `Token ${token}` },
        }),
      ]);

      if (automationResponse.ok && jobResponse.ok) {
        const [automationData, jobData] = await Promise.all([
          automationResponse.json(),
          jobResponse.json(),
        ]);

        setStats({
          ...automationData,
          ...jobData,
        });
      }
    } catch (error) {
      console.error("Error fetching dashboard stats:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    router.push("/");
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold">HJ</span>
          </div>
          <p className="text-gray-600 dark:text-gray-400">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  const successRate = stats?.total_applications ? 
    Math.round((stats.successful_applications / stats.total_applications) * 100) : 0;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Navigation */}
      <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">HJ</span>
              </div>
              <span className="text-xl font-bold text-gray-900 dark:text-white">HopeForJob</span>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600 dark:text-gray-400">
                Welcome, {user?.first_name || user?.username}!
              </span>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400">Monitor your automated job applications and track your progress</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Total Applications
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats?.total_applications || 0}
                </span>
                <Briefcase className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Success Rate
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold text-green-600">
                  {successRate}%
                </span>
                <Target className="h-8 w-8 text-green-600" />
              </div>
              <Progress value={successRate} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Active Sessions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold text-orange-600">
                  {stats?.active_sessions || 0}
                </span>
                <TrendingUp className="h-8 w-8 text-orange-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Saved Jobs
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold text-purple-600">
                  {stats?.total_saved_jobs || 0}
                </span>
                <Heart className="h-8 w-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Start automating your job applications</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button className="w-full justify-start" onClick={() => router.push("/jobs")}>
                <Search className="mr-2 h-4 w-4" />
                Browse Jobs
              </Button>
              <Button variant="outline" className="w-full justify-start" onClick={() => router.push("/automation")}>
                <Play className="mr-2 h-4 w-4" />
                Start Automation
              </Button>
              <Button variant="outline" className="w-full justify-start" onClick={() => router.push("/profile")}>
                <Settings className="mr-2 h-4 w-4" />
                Update Profile
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>Your latest application activities</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {stats?.total_applications === 0 ? (
                  <div className="text-center text-gray-500 py-8">
                    <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p>No applications yet</p>
                    <p className="text-sm">Start by browsing jobs or setting up automation</p>
                  </div>
                ) : (
                  <>
                    <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="h-5 w-5 text-green-600" />
                        <span className="text-sm text-green-800 dark:text-green-200">
                          {stats?.successful_applications} successful applications
                        </span>
                      </div>
                      <Badge variant="secondary">Success</Badge>
                    </div>
                    
                    {stats && stats.pending_applications > 0 && (
                      <div className="flex items-center justify-between p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <Play className="h-5 w-5 text-yellow-600" />
                          <span className="text-sm text-yellow-800 dark:text-yellow-200">
                            {stats.pending_applications} applications pending
                          </span>
                        </div>
                        <Badge variant="outline">Pending</Badge>
                      </div>
                    )}
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Navigation Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => router.push("/jobs")}>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Search className="mr-2 h-5 w-5" />
                Job Search
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 dark:text-gray-400">
                Browse and search for job opportunities across multiple platforms
              </p>
            </CardContent>
          </Card>

          <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => router.push("/automation")}>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Play className="mr-2 h-5 w-5" />
                Automation
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 dark:text-gray-400">
                Set up and manage automated job applications and rules
              </p>
            </CardContent>
          </Card>

          <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => router.push("/profile")}>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="mr-2 h-5 w-5" />
                Profile
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 dark:text-gray-400">
                Manage your profile, resume, and application preferences
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
