import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowRight, Zap, Target, Users, TrendingUp } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* Navigation */}
      <nav className="container mx-auto px-4 py-6 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">HJ</span>
          </div>
          <span className="text-xl font-bold text-gray-900 dark:text-white">HopeForJob</span>
        </div>
        <div className="flex items-center space-x-4">
          <Link href="/auth/login">
            <Button variant="ghost">Login</Button>
          </Link>
          <Link href="/auth/register">
            <Button>Get Started</Button>
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <Badge className="mb-4" variant="secondary">
          🚀 Automated Job Applications
        </Badge>
        <h1 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
          Your Personal
          <span className="text-blue-600 block">Job Application Assistant</span>
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
          Automate your job search with intelligent applications to LinkedIn and other platforms. 
          Save time, increase applications, and land your dream job faster.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/auth/register">
            <Button size="lg" className="w-full sm:w-auto">
              Start Applying Now <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
          <Link href="/demo">
            <Button size="lg" variant="outline" className="w-full sm:w-auto">
              Watch Demo
            </Button>
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-20">
        <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">
          Why Choose HopeForJob?
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="text-center">
            <CardHeader>
              <Zap className="h-12 w-12 text-blue-600 mx-auto mb-4" />
              <CardTitle>Lightning Fast</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Apply to hundreds of jobs in minutes, not hours. Our automation handles the repetitive work.
              </CardDescription>
            </CardContent>
          </Card>
          
          <Card className="text-center">
            <CardHeader>
              <Target className="h-12 w-12 text-green-600 mx-auto mb-4" />
              <CardTitle>Smart Targeting</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                AI-powered job matching ensures you only apply to positions that fit your profile and preferences.
              </CardDescription>
            </CardContent>
          </Card>
          
          <Card className="text-center">
            <CardHeader>
              <Users className="h-12 w-12 text-purple-600 mx-auto mb-4" />
              <CardTitle>Multi-Platform</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Support for LinkedIn, Indeed, and other major job platforms. Expand your reach effortlessly.
              </CardDescription>
            </CardContent>
          </Card>
          
          <Card className="text-center">
            <CardHeader>
              <TrendingUp className="h-12 w-12 text-orange-600 mx-auto mb-4" />
              <CardTitle>Track Progress</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Comprehensive analytics and tracking to optimize your job search strategy and increase success rates.
              </CardDescription>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-20">
        <Card className="bg-blue-600 text-white">
          <CardContent className="p-12 text-center">
            <h3 className="text-3xl font-bold mb-4">Ready to Transform Your Job Search?</h3>
            <p className="text-xl text-blue-100 mb-8">
              Join thousands of job seekers who have automated their way to success.
            </p>
            <Link href="/auth/register">
              <Button size="lg" variant="secondary">
                Get Started Free <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </CardContent>
        </Card>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-700">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <div className="w-6 h-6 bg-blue-600 rounded flex items-center justify-center">
                <span className="text-white font-bold text-xs">HJ</span>
              </div>
              <span className="text-gray-600 dark:text-gray-400">© 2025 HopeForJob. All rights reserved.</span>
            </div>
            <div className="flex space-x-6">
              <Link href="/privacy" className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">
                Privacy
              </Link>
              <Link href="/terms" className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">
                Terms
              </Link>
              <Link href="/support" className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">
                Support
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
