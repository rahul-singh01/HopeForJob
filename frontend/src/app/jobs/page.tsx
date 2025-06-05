"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { 
  Search, 
  MapPin, 
  Building, 
  Clock, 
  Heart, 
  ExternalLink,
  Filter,
  Briefcase,
  DollarSign
} from "lucide-react";
import { jobsAPI, isAuthenticated } from "@/lib/api";
import { toast } from "sonner";

interface Job {
  id: number;
  title: string;
  company_name: string; // Updated field name to match backend
  location: string;
  description: string;
  salary_min?: number;
  salary_max?: number;
  employment_type: string; // Updated field name to match backend
  experience_level: string;
  url: string;
  scraped_at: string; // Updated field name to match backend
  source: {
    name: string;
  };
}

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [location, setLocation] = useState("");
  const [jobType, setJobType] = useState("");
  const [savedJobs, setSavedJobs] = useState<Set<number>>(new Set());
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/auth/login");
      return;
    }
    
    fetchJobs();
    fetchSavedJobs();
  }, [router]);

  const fetchJobs = async (search?: string, loc?: string, type?: string) => {
    try {
      setIsLoading(true);
      const params: any = {};
      if (search) params.search = search;
      if (loc) params.location = loc;
      if (type) params.employment_type = type;

      const response = await jobsAPI.getListings(params);
      const data = response.data;
      setJobs(data.results || data);
    } catch (error) {
      console.error("Error fetching jobs:", error);
      toast.error("Failed to fetch jobs");
    } finally {
      setIsLoading(false);
    }
  };

  const fetchSavedJobs = async () => {
    try {
      const response = await jobsAPI.getSavedJobs();
      const data = response.data;
      
      // Handle both paginated and non-paginated responses
      const savedJobsArray = data.results || data;
      
      // Ensure we have an array before mapping
      if (Array.isArray(savedJobsArray)) {
        const saved = new Set(savedJobsArray.map((item: any) => item.job.id as number));
        setSavedJobs(saved);
      } else {
        console.warn("Expected array but got:", savedJobsArray);
        setSavedJobs(new Set());
      }
    } catch (error) {
      console.error("Error fetching saved jobs:", error);
      toast.error("Failed to fetch saved jobs");
    }
  };

  const handleSearch = () => {
    fetchJobs(searchQuery, location, jobType);
  };

  const handleSaveJob = async (jobId: number) => {
    try {
      if (savedJobs.has(jobId)) {
        // Unsave job - first get saved jobs to find the ID
        const response = await jobsAPI.getSavedJobs();
        const data = response.data;
        const savedJob = data.find((item: any) => item.job.id === jobId);
        
        if (savedJob) {
          await jobsAPI.unsaveJob(savedJob.id);
          setSavedJobs(prev => {
            const newSet = new Set(prev);
            newSet.delete(jobId);
            return newSet;
          });
          toast.success("Job removed from saved");
        }
      } else {
        // Save job
        await jobsAPI.saveJob(jobId);
        setSavedJobs(prev => new Set([...prev, jobId]));
        toast.success("Job saved successfully");
      }
    } catch (error) {
      console.error("Error saving/unsaving job:", error);
      toast.error("Failed to save/unsave job");
    }
  };

  const formatSalary = (min?: number, max?: number) => {
    if (!min && !max) return null;
    if (min && max) return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
    if (min) return `$${min.toLocaleString()}+`;
    if (max) return `Up to $${max.toLocaleString()}`;
  };

  const getJobTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case "full_time": return "bg-green-100 text-green-800";
      case "part_time": return "bg-blue-100 text-blue-800";
      case "contract": return "bg-purple-100 text-purple-800";
      case "internship": return "bg-orange-100 text-orange-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Navigation */}
      <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center cursor-pointer" onClick={() => router.push("/dashboard")}>
                <span className="text-white font-bold text-sm">HJ</span>
              </div>
              <span className="text-xl font-bold text-gray-900 dark:text-white">Jobs</span>
            </div>
            
            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm" onClick={() => router.push("/dashboard")}>
                Dashboard
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">Find Your Next Job</h1>
          
          <Card>
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="md:col-span-2">
                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Search jobs, companies, or keywords..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                      onKeyPress={(e) => e.key === "Enter" && handleSearch()}
                    />
                  </div>
                </div>
                
                <div className="relative">
                  <MapPin className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Location"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    className="pl-10"
                    onKeyPress={(e) => e.key === "Enter" && handleSearch()}
                  />
                </div>
                
                <Select value={jobType || "all"} onValueChange={(value) => setJobType(value === "all" ? "" : value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Job Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    <SelectItem value="full_time">Full Time</SelectItem>
                    <SelectItem value="part_time">Part Time</SelectItem>
                    <SelectItem value="contract">Contract</SelectItem>
                    <SelectItem value="internship">Internship</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="flex justify-between items-center mt-4">
                <Button onClick={handleSearch} disabled={isLoading}>
                  {isLoading ? "Searching..." : "Search Jobs"}
                </Button>
                
                <Button variant="outline" onClick={() => router.push("/jobs/scrape")}>
                  <Filter className="mr-2 h-4 w-4" />
                  Scrape New Jobs
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Job Listings */}
        <div className="space-y-4">
          {isLoading ? (
            <div className="text-center py-12">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold">HJ</span>
              </div>
              <p className="text-gray-600 dark:text-gray-400">Loading jobs...</p>
            </div>
          ) : jobs.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <Briefcase className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No jobs found</h3>
                <p className="text-gray-600 dark:text-gray-400">Try adjusting your search criteria or scrape new jobs.</p>
              </CardContent>
            </Card>
          ) : (
            jobs.map((job) => (
              <Card key={job.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                          {job.title}
                        </h3>
                        <Badge className={getJobTypeColor(job.employment_type)}>
                          {job.employment_type.replace("_", " ")}
                        </Badge>
                      </div>
                      
                      <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400 mb-3">
                        <div className="flex items-center">
                          <Building className="h-4 w-4 mr-1" />
                          {job.company_name}
                        </div>
                        <div className="flex items-center">
                          <MapPin className="h-4 w-4 mr-1" />
                          {job.location}
                        </div>
                        <div className="flex items-center">
                          <Clock className="h-4 w-4 mr-1" />
                          {new Date(job.scraped_at).toLocaleDateString()}
                        </div>
                      </div>
                      
                      {formatSalary(job.salary_min, job.salary_max) && (
                        <div className="flex items-center text-sm text-green-600 mb-3">
                          <DollarSign className="h-4 w-4 mr-1" />
                          {formatSalary(job.salary_min, job.salary_max)}
                        </div>
                      )}
                      
                      <p className="text-gray-700 dark:text-gray-300 mb-4 line-clamp-3">
                        {job.description}
                      </p>
                      
                      <div className="flex items-center justify-between">
                        <Badge variant="outline">{job.source.name}</Badge>
                        <div className="flex space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleSaveJob(job.id)}
                            className={savedJobs.has(job.id) ? "text-red-600" : ""}
                          >
                            <Heart className={`h-4 w-4 mr-1 ${savedJobs.has(job.id) ? "fill-current" : ""}`} />
                            {savedJobs.has(job.id) ? "Saved" : "Save"}
                          </Button>
                          <Button size="sm" onClick={() => window.open(job.url, "_blank")}>
                            <ExternalLink className="h-4 w-4 mr-1" />
                            View Job
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
