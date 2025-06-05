'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { 
  Settings, 
  Bell, 
  Shield, 
  Key, 
  Palette, 
  Globe, 
  Download,
  Trash2,
  AlertTriangle,
  Save
} from 'lucide-react'

interface NotificationSettings {
  email_notifications: boolean
  push_notifications: boolean
  application_updates: boolean
  job_alerts: boolean
  weekly_summary: boolean
}

interface PrivacySettings {
  profile_visibility: 'public' | 'private' | 'limited'
  share_analytics: boolean
  data_retention: number
}

interface AppSettings {
  theme: 'light' | 'dark' | 'system'
  language: string
  timezone: string
  auto_save: boolean
}

export default function SettingsPage() {
  const [notifications, setNotifications] = useState<NotificationSettings>({
    email_notifications: true,
    push_notifications: true,
    application_updates: true,
    job_alerts: true,
    weekly_summary: false
  })
  
  const [privacy, setPrivacy] = useState<PrivacySettings>({
    profile_visibility: 'private',
    share_analytics: false,
    data_retention: 365
  })
  
  const [appSettings, setAppSettings] = useState<AppSettings>({
    theme: 'system',
    language: 'en',
    timezone: 'UTC',
    auto_save: true
  })
  
  const [apiKeys, setApiKeys] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [newApiKey, setNewApiKey] = useState('')

  const saveSettings = async (settingsType: 'notifications' | 'privacy' | 'app') => {
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const token = localStorage.getItem('token')
      let data
      let endpoint

      switch (settingsType) {
        case 'notifications':
          data = notifications
          endpoint = 'notification-settings'
          break
        case 'privacy':
          data = privacy
          endpoint = 'privacy-settings'
          break
        case 'app':
          data = appSettings
          endpoint = 'app-settings'
          break
      }

      // In a real app, you would make an API call here
      // await axios.post(`http://localhost:8000/api/settings/${endpoint}/`, data, {
      //   headers: { Authorization: `Token ${token}` }
      // })

      setSuccess(`${settingsType.charAt(0).toUpperCase() + settingsType.slice(1)} settings saved successfully!`)
    } catch (error) {
      setError('Failed to save settings')
      console.error('Error saving settings:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateApiKey = async () => {
    try {
      const token = localStorage.getItem('token')
      // In a real app, you would make an API call here
      const newKey = {
        id: Date.now(),
        name: 'New API Key',
        key: 'hfj_' + Math.random().toString(36).substring(2, 15),
        created_at: new Date().toISOString(),
        last_used: null
      }
      setApiKeys(prev => [...prev, newKey])
      setSuccess('API key generated successfully!')
    } catch (error) {
      setError('Failed to generate API key')
      console.error('Error generating API key:', error)
    }
  }

  const deleteApiKey = async (keyId: number) => {
    try {
      const token = localStorage.getItem('token')
      // In a real app, you would make an API call here
      setApiKeys(prev => prev.filter(key => key.id !== keyId))
      setSuccess('API key deleted successfully!')
    } catch (error) {
      setError('Failed to delete API key')
      console.error('Error deleting API key:', error)
    }
  }

  const exportData = async () => {
    try {
      const token = localStorage.getItem('token')
      // In a real app, you would make an API call here
      const data = {
        profile: {},
        applications: [],
        settings: { notifications, privacy, appSettings }
      }
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `hopeforjob-data-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      
      setSuccess('Data exported successfully!')
    } catch (error) {
      setError('Failed to export data')
      console.error('Error exporting data:', error)
    }
  }

  const deleteAccount = async () => {
    if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      try {
        const token = localStorage.getItem('token')
        // In a real app, you would make an API call here
        // await axios.delete('http://localhost:8000/api/auth/account/', {
        //   headers: { Authorization: `Token ${token}` }
        // })
        
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        window.location.href = '/auth/login'
      } catch (error) {
        setError('Failed to delete account')
        console.error('Error deleting account:', error)
      }
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Settings</h1>
          <p className="text-muted-foreground">
            Manage your account settings and preferences
          </p>
        </div>

        {error && (
          <Alert className="mb-6" variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mb-6">
            <AlertDescription>{success}</AlertDescription>
          </Alert>
        )}

        <Tabs defaultValue="notifications" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="notifications">Notifications</TabsTrigger>
            <TabsTrigger value="privacy">Privacy</TabsTrigger>
            <TabsTrigger value="appearance">Appearance</TabsTrigger>
            <TabsTrigger value="api">API Keys</TabsTrigger>
            <TabsTrigger value="account">Account</TabsTrigger>
          </TabsList>

          <TabsContent value="notifications">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bell className="h-5 w-5" />
                  Notification Preferences
                </CardTitle>
                <CardDescription>
                  Choose how you want to be notified about job applications and updates
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Email Notifications</Label>
                      <p className="text-sm text-muted-foreground">
                        Receive notifications via email
                      </p>
                    </div>
                    <Switch
                      checked={notifications.email_notifications}
                      onCheckedChange={(checked) => 
                        setNotifications(prev => ({ ...prev, email_notifications: checked }))
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Push Notifications</Label>
                      <p className="text-sm text-muted-foreground">
                        Receive push notifications in your browser
                      </p>
                    </div>
                    <Switch
                      checked={notifications.push_notifications}
                      onCheckedChange={(checked) => 
                        setNotifications(prev => ({ ...prev, push_notifications: checked }))
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Application Updates</Label>
                      <p className="text-sm text-muted-foreground">
                        Get notified when applications are submitted or updated
                      </p>
                    </div>
                    <Switch
                      checked={notifications.application_updates}
                      onCheckedChange={(checked) => 
                        setNotifications(prev => ({ ...prev, application_updates: checked }))
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Job Alerts</Label>
                      <p className="text-sm text-muted-foreground">
                        Receive alerts for new job matches
                      </p>
                    </div>
                    <Switch
                      checked={notifications.job_alerts}
                      onCheckedChange={(checked) => 
                        setNotifications(prev => ({ ...prev, job_alerts: checked }))
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Weekly Summary</Label>
                      <p className="text-sm text-muted-foreground">
                        Get a weekly summary of your job search activity
                      </p>
                    </div>
                    <Switch
                      checked={notifications.weekly_summary}
                      onCheckedChange={(checked) => 
                        setNotifications(prev => ({ ...prev, weekly_summary: checked }))
                      }
                    />
                  </div>
                </div>

                <Button onClick={() => saveSettings('notifications')} disabled={loading}>
                  <Save className="h-4 w-4 mr-2" />
                  {loading ? 'Saving...' : 'Save Notification Settings'}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="privacy">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Privacy Settings
                </CardTitle>
                <CardDescription>
                  Control how your data is used and shared
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>Profile Visibility</Label>
                    <Select
                      value={privacy.profile_visibility}
                      onValueChange={(value: any) => 
                        setPrivacy(prev => ({ ...prev, profile_visibility: value }))
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="public">Public - Visible to everyone</SelectItem>
                        <SelectItem value="limited">Limited - Visible to approved connections</SelectItem>
                        <SelectItem value="private">Private - Only visible to you</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Share Analytics</Label>
                      <p className="text-sm text-muted-foreground">
                        Help improve our service by sharing anonymized usage data
                      </p>
                    </div>
                    <Switch
                      checked={privacy.share_analytics}
                      onCheckedChange={(checked) => 
                        setPrivacy(prev => ({ ...prev, share_analytics: checked }))
                      }
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Data Retention (days)</Label>
                    <Select
                      value={privacy.data_retention.toString()}
                      onValueChange={(value) => 
                        setPrivacy(prev => ({ ...prev, data_retention: parseInt(value) }))
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="30">30 days</SelectItem>
                        <SelectItem value="90">90 days</SelectItem>
                        <SelectItem value="365">1 year</SelectItem>
                        <SelectItem value="999999">Forever</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <Button onClick={() => saveSettings('privacy')} disabled={loading}>
                  <Save className="h-4 w-4 mr-2" />
                  {loading ? 'Saving...' : 'Save Privacy Settings'}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="appearance">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Palette className="h-5 w-5" />
                  Appearance & Language
                </CardTitle>
                <CardDescription>
                  Customize how the application looks and feels
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>Theme</Label>
                    <Select
                      value={appSettings.theme}
                      onValueChange={(value: any) => 
                        setAppSettings(prev => ({ ...prev, theme: value }))
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="light">Light</SelectItem>
                        <SelectItem value="dark">Dark</SelectItem>
                        <SelectItem value="system">System</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Language</Label>
                    <Select
                      value={appSettings.language}
                      onValueChange={(value) => 
                        setAppSettings(prev => ({ ...prev, language: value }))
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="en">English</SelectItem>
                        <SelectItem value="es">Spanish</SelectItem>
                        <SelectItem value="fr">French</SelectItem>
                        <SelectItem value="de">German</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Timezone</Label>
                    <Select
                      value={appSettings.timezone}
                      onValueChange={(value) => 
                        setAppSettings(prev => ({ ...prev, timezone: value }))
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="UTC">UTC</SelectItem>
                        <SelectItem value="America/New_York">Eastern Time</SelectItem>
                        <SelectItem value="America/Chicago">Central Time</SelectItem>
                        <SelectItem value="America/Denver">Mountain Time</SelectItem>
                        <SelectItem value="America/Los_Angeles">Pacific Time</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Auto-save</Label>
                      <p className="text-sm text-muted-foreground">
                        Automatically save changes as you type
                      </p>
                    </div>
                    <Switch
                      checked={appSettings.auto_save}
                      onCheckedChange={(checked) => 
                        setAppSettings(prev => ({ ...prev, auto_save: checked }))
                      }
                    />
                  </div>
                </div>

                <Button onClick={() => saveSettings('app')} disabled={loading}>
                  <Save className="h-4 w-4 mr-2" />
                  {loading ? 'Saving...' : 'Save Appearance Settings'}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="api">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Key className="h-5 w-5" />
                  API Keys
                </CardTitle>
                <CardDescription>
                  Manage API keys for integrating with external services
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-lg font-medium">Your API Keys</h3>
                    <p className="text-sm text-muted-foreground">
                      Use these keys to access HopeForJob API programmatically
                    </p>
                  </div>
                  <Button onClick={generateApiKey}>
                    <Key className="h-4 w-4 mr-2" />
                    Generate New Key
                  </Button>
                </div>

                <div className="space-y-4">
                  {apiKeys.map((key) => (
                    <div key={key.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <div className="font-medium">{key.name}</div>
                        <div className="text-sm text-muted-foreground font-mono">
                          {key.key}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          Created {new Date(key.created_at).toLocaleDateString()}
                        </div>
                      </div>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => deleteApiKey(key.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                  
                  {apiKeys.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      No API keys generated yet. Click "Generate New Key" to create one.
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="account">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  Account Management
                </CardTitle>
                <CardDescription>
                  Manage your account data and preferences
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="p-4 border rounded-lg">
                    <h3 className="font-medium mb-2">Export Your Data</h3>
                    <p className="text-sm text-muted-foreground mb-4">
                      Download a copy of all your data including profile, applications, and settings
                    </p>
                    <Button onClick={exportData} variant="outline">
                      <Download className="h-4 w-4 mr-2" />
                      Export Data
                    </Button>
                  </div>

                  <Separator />

                  <div className="p-4 border border-red-200 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <AlertTriangle className="h-5 w-5 text-red-600" />
                      <h3 className="font-medium text-red-600">Danger Zone</h3>
                    </div>
                    <p className="text-sm text-muted-foreground mb-4">
                      Once you delete your account, there is no going back. Please be certain.
                    </p>
                    <Button onClick={deleteAccount} variant="destructive">
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete Account
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
