'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { Switch } from '@/components/ui/switch'
import { 
  Play, 
  Pause, 
  Square, 
  Settings, 
  Plus, 
  Calendar, 
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Bot,
  Target,
  Zap,
  BarChart3
} from 'lucide-react'
import { automationAPI } from '@/lib/api'
import { toast } from "sonner";

interface AutomationSession {
  id?: number
  name: string
  target_platforms: string[]
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed'
  applications_sent: number
  applications_limit: number
  daily_limit: number
  created_at?: string
  updated_at?: string
  is_active: boolean
  search_keywords: string[]
  location_filters: string[]
  salary_min?: number
  salary_max?: number
  experience_level: string[]
  job_types: string[]
}

interface JobApplication {
  id: number
  job_title: string
  company: string
  platform: string
  status: 'pending' | 'applied' | 'failed'
  applied_at?: string
  error_message?: string
}

const STATUS_COLORS = {
  pending: 'bg-yellow-100 text-yellow-800',
  running: 'bg-blue-100 text-blue-800',
  paused: 'bg-gray-100 text-gray-800',
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800'
}

const STATUS_ICONS = {
  pending: Clock,
  running: Play,
  paused: Pause,
  completed: CheckCircle,
  failed: XCircle
}

export default function AutomationPage() {
  const [sessions, setSessions] = useState<AutomationSession[]>([])
  const [applications, setApplications] = useState<JobApplication[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [newSession, setNewSession] = useState<AutomationSession>({
    name: '',
    target_platforms: [],
    status: 'pending',
    applications_sent: 0,
    applications_limit: 50,
    daily_limit: 10,
    is_active: true,
    search_keywords: [],
    location_filters: [],
    experience_level: [],
    job_types: []
  })

  useEffect(() => {
    fetchSessions()
    fetchApplications()
  }, [])

  const fetchSessions = async () => {
    try {
      const data = await automationAPI.getSessions()
      // Handle both paginated and non-paginated responses
      setSessions(data.results || data || [])
    } catch (error) {
      console.error('Error fetching sessions:', error)
      toast.error("Failed to load automation sessions")
    }
  }

  const fetchApplications = async () => {
    try {
      const data = await automationAPI.getApplications()
      // Handle both paginated and non-paginated responses
      setApplications(data.results || data || [])
    } catch (error) {
      console.error('Error fetching applications:', error)
      toast.error("Failed to load job applications")
    } finally {
      setLoading(false)
    }
  }

  const createSession = async () => {
    setCreating(true)

    try {
      await automationAPI.createSession(newSession)
      
      toast.success("Automation session created successfully!")
      
      setNewSession({
        name: '',
        target_platforms: [],
        status: 'pending',
        applications_sent: 0,
        applications_limit: 50,
        daily_limit: 10,
        is_active: true,
        search_keywords: [],
        location_filters: [],
        experience_level: [],
        job_types: []
      })
      fetchSessions()
    } catch (error) {
      toast.error("Failed to create automation session")
      console.error('Error creating session:', error)
    } finally {
      setCreating(false)
    }
  }

  const controlSession = async (sessionId: number, action: 'start' | 'pause' | 'stop') => {
    try {
      await automationAPI.controlSession(sessionId, action)
      fetchSessions()
      toast.success(`Session ${action}ed successfully!`)
    } catch (error) {
      toast.error(`Failed to ${action} session`)
      console.error(`Error ${action}ing session:`, error)
    }
  }

  const addKeyword = (keyword: string) => {
    if (keyword.trim() && !newSession.search_keywords.includes(keyword.trim())) {
      setNewSession(prev => ({
        ...prev,
        search_keywords: [...prev.search_keywords, keyword.trim()]
      }))
    }
  }

  const removeKeyword = (keyword: string) => {
    setNewSession(prev => ({
      ...prev,
      search_keywords: prev.search_keywords.filter(k => k !== keyword)
    }))
  }

  const togglePlatform = (platform: string) => {
    setNewSession(prev => ({
      ...prev,
      target_platforms: prev.target_platforms.includes(platform)
        ? prev.target_platforms.filter(p => p !== platform)
        : [...prev.target_platforms, platform]
    }))
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">Loading automation data...</div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Job Application Automation</h1>
          <p className="text-muted-foreground">
            Manage automated job applications across different platforms
          </p>
        </div>

        <Tabs defaultValue="sessions" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="sessions">Automation Sessions</TabsTrigger>
            <TabsTrigger value="applications">Recent Applications</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="sessions">
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold">Active Sessions</h2>
                <Dialog>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="h-4 w-4 mr-2" />
                      Create New Session
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-2xl">
                    <DialogHeader>
                      <DialogTitle>Create Automation Session</DialogTitle>
                      <DialogDescription>
                        Set up a new automated job application session
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label>Session Name</Label>
                        <Input
                          value={newSession.name}
                          onChange={(e) => setNewSession(prev => ({ ...prev, name: e.target.value }))}
                          placeholder="e.g., Frontend Developer - Remote"
                        />
                      </div>

                      <div className="space-y-2">
                        <Label>Target Platforms</Label>
                        <div className="grid grid-cols-2 gap-2">
                          {['LinkedIn', 'Indeed', 'Glassdoor', 'ZipRecruiter'].map((platform) => (
                            <div key={platform} className="flex items-center space-x-2">
                              <Switch
                                checked={newSession.target_platforms.includes(platform)}
                                onCheckedChange={() => togglePlatform(platform)}
                              />
                              <Label>{platform}</Label>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Daily Application Limit</Label>
                          <Input
                            type="number"
                            value={newSession.daily_limit}
                            onChange={(e) => setNewSession(prev => ({ ...prev, daily_limit: parseInt(e.target.value) }))}
                            min="1"
                            max="50"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Total Application Limit</Label>
                          <Input
                            type="number"
                            value={newSession.applications_limit}
                            onChange={(e) => setNewSession(prev => ({ ...prev, applications_limit: parseInt(e.target.value) }))}
                            min="1"
                          />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label>Search Keywords</Label>
                        <div className="flex flex-wrap gap-2 mb-2">
                          {newSession.search_keywords.map((keyword) => (
                            <Badge key={keyword} variant="secondary" className="flex items-center gap-1">
                              {keyword}
                              <button
                                onClick={() => removeKeyword(keyword)}
                                className="ml-1 text-xs hover:text-red-500"
                              >
                                ×
                              </button>
                            </Badge>
                          ))}
                        </div>
                        <Input
                          placeholder="Add keywords (press Enter)"
                          onKeyPress={(e) => {
                            if (e.key === 'Enter') {
                              addKeyword(e.currentTarget.value)
                              e.currentTarget.value = ''
                            }
                          }}
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Minimum Salary ($)</Label>
                          <Input
                            type="number"
                            value={newSession.salary_min || ''}
                            onChange={(e) => setNewSession(prev => ({ ...prev, salary_min: parseInt(e.target.value) }))}
                            placeholder="50000"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Maximum Salary ($)</Label>
                          <Input
                            type="number"
                            value={newSession.salary_max || ''}
                            onChange={(e) => setNewSession(prev => ({ ...prev, salary_max: parseInt(e.target.value) }))}
                            placeholder="100000"
                          />
                        </div>
                      </div>

                      <Button onClick={createSession} disabled={creating} className="w-full">
                        {creating ? 'Creating...' : 'Create Session'}
                      </Button>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>

              <div className="grid gap-6">
                {sessions.map((session) => {
                  const StatusIcon = STATUS_ICONS[session.status]
                  const progress = session.applications_limit > 0 
                    ? (session.applications_sent / session.applications_limit) * 100 
                    : 0

                  return (
                    <Card key={session.id}>
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className={`p-2 rounded-full ${STATUS_COLORS[session.status]}`}>
                              <StatusIcon className="h-4 w-4" />
                            </div>
                            <div>
                              <CardTitle>{session.name}</CardTitle>
                              <CardDescription>
                                {session.target_platforms.join(', ')} • 
                                Created {session.created_at ? new Date(session.created_at).toLocaleDateString() : 'Recently'}
                              </CardDescription>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            {session.status === 'pending' || session.status === 'paused' ? (
                              <Button
                                size="sm"
                                onClick={() => session.id && controlSession(session.id, 'start')}
                              >
                                <Play className="h-4 w-4 mr-1" />
                                Start
                              </Button>
                            ) : null}
                            {session.status === 'running' ? (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => session.id && controlSession(session.id, 'pause')}
                              >
                                <Pause className="h-4 w-4 mr-1" />
                                Pause
                              </Button>
                            ) : null}
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => session.id && controlSession(session.id, 'stop')}
                            >
                              <Square className="h-4 w-4 mr-1" />
                              Stop
                            </Button>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div className="text-center">
                              <div className="text-2xl font-bold text-blue-600">
                                {session.applications_sent}
                              </div>
                              <div className="text-sm text-muted-foreground">Applications Sent</div>
                            </div>
                            <div className="text-center">
                              <div className="text-2xl font-bold text-green-600">
                                {session.applications_limit}
                              </div>
                              <div className="text-sm text-muted-foreground">Limit</div>
                            </div>
                            <div className="text-center">
                              <div className="text-2xl font-bold text-orange-600">
                                {session.daily_limit}
                              </div>
                              <div className="text-sm text-muted-foreground">Daily Limit</div>
                            </div>
                            <div className="text-center">
                              <div className="text-2xl font-bold text-purple-600">
                                {Math.round(progress)}%
                              </div>
                              <div className="text-sm text-muted-foreground">Progress</div>
                            </div>
                          </div>
                          
                          <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                              <span>Progress</span>
                              <span>{session.applications_sent} / {session.applications_limit}</span>
                            </div>
                            <Progress value={progress} className="h-2" />
                          </div>

                          {session.search_keywords.length > 0 && (
                            <div className="space-y-2">
                              <Label className="text-sm font-medium">Keywords:</Label>
                              <div className="flex flex-wrap gap-1">
                                {session.search_keywords.map((keyword) => (
                                  <Badge key={keyword} variant="outline" className="text-xs">
                                    {keyword}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  )
                })}

                {sessions.length === 0 && (
                  <Card>
                    <CardContent className="text-center py-12">
                      <Bot className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                      <h3 className="text-lg font-semibold mb-2">No Automation Sessions</h3>
                      <p className="text-muted-foreground mb-4">
                        Create your first automation session to start applying to jobs automatically
                      </p>
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button>
                            <Plus className="h-4 w-4 mr-2" />
                            Create Your First Session
                          </Button>
                        </DialogTrigger>
                      </Dialog>
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="applications">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  Recent Applications
                </CardTitle>
                <CardDescription>
                  Track your automated job applications
                </CardDescription>
              </CardHeader>
              <CardContent>
                {applications.length > 0 ? (
                  <div className="space-y-4">
                    {applications.map((app) => (
                      <div key={app.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex-1">
                          <h3 className="font-semibold">{app.job_title}</h3>
                          <p className="text-muted-foreground">{app.company} • {app.platform}</p>
                          {app.applied_at && (
                            <p className="text-sm text-muted-foreground">
                              Applied {new Date(app.applied_at).toLocaleDateString()}
                            </p>
                          )}
                          {app.error_message && (
                            <p className="text-sm text-red-600 mt-1">{app.error_message}</p>
                          )}
                        </div>
                        <Badge
                          variant={app.status === 'applied' ? 'default' : 
                                  app.status === 'failed' ? 'destructive' : 'secondary'}
                        >
                          {app.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <AlertCircle className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                    <h3 className="text-lg font-semibold mb-2">No Applications Yet</h3>
                    <p className="text-muted-foreground">
                      Your automated applications will appear here once you start a session
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Analytics Dashboard
                </CardTitle>
                <CardDescription>
                  Track your automation performance and success rates
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-muted-foreground">
                  <Zap className="h-12 w-12 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Analytics Coming Soon</h3>
                  <p>
                    Detailed analytics and insights will be available once you have automation data
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
