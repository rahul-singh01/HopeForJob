'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { User, MapPin, Phone, Mail, Calendar, Plus, Edit, Trash2, Save, Building, GraduationCap, FileText } from 'lucide-react'
import { profileAPI } from '@/lib/api'

interface UserProfile {
  id?: number
  phone?: string
  location?: string
  bio?: string
  skills?: string[]
  experience_years?: number
  preferred_salary_min?: number
  preferred_salary_max?: string
  preferred_locations?: string[]
  availability?: string
}

interface Experience {
  id?: number
  company: string
  position: string
  start_date: string
  end_date?: string
  description?: string
  is_current: boolean
}

interface Education {
  id?: number
  institution: string
  degree: string
  field_of_study: string
  start_date: string
  end_date?: string
  grade?: string
  is_current: boolean
}

interface ApplicationTemplate {
  id?: number
  name: string
  cover_letter_template: string
  is_default: boolean
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile>({})
  const [experiences, setExperiences] = useState<Experience[]>([])
  const [education, setEducation] = useState<Education[]>([])
  const [templates, setTemplates] = useState<ApplicationTemplate[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [newSkill, setNewSkill] = useState('')
  const [editingExperience, setEditingExperience] = useState<Experience | null>(null)
  const [editingEducation, setEditingEducation] = useState<Education | null>(null)
  const [editingTemplate, setEditingTemplate] = useState<ApplicationTemplate | null>(null)

  useEffect(() => {
    fetchProfile()
    fetchExperiences()
    fetchEducation()
    fetchTemplates()
  }, [])

  const fetchProfile = async () => {
    try {
      const response = await profileAPI.getProfile()
      setProfile(response.data)
    } catch (error) {
      console.error('Error fetching profile:', error)
      setError('Failed to load profile')
    }
  }

  const fetchExperiences = async () => {
    try {
      const response = await profileAPI.getExperience()
      setExperiences(response.data)
    } catch (error) {
      console.error('Error fetching experiences:', error)
    }
  }

  const fetchEducation = async () => {
    try {
      const response = await profileAPI.getEducation()
      setEducation(response.data)
    } catch (error) {
      console.error('Error fetching education:', error)
    }
  }

  const fetchTemplates = async () => {
    try {
      const response = await profileAPI.getTemplates()
      setTemplates(response.data)
    } catch (error) {
      console.error('Error fetching templates:', error)
    } finally {
      setLoading(false)
    }
  }

  const saveProfile = async () => {
    setSaving(true)
    setError('')
    setSuccess('')
    
    try {
      await profileAPI.updateProfile(profile)
      setSuccess('Profile updated successfully!')
      fetchProfile()
    } catch (error) {
      setError('Failed to save profile')
      console.error('Error saving profile:', error)
    } finally {
      setSaving(false)
    }
  }

  const addSkill = () => {
    if (newSkill.trim() && !profile.skills?.includes(newSkill.trim())) {
      setProfile(prev => ({
        ...prev,
        skills: [...(prev.skills || []), newSkill.trim()]
      }))
      setNewSkill('')
    }
  }

  const removeSkill = (skill: string) => {
    setProfile(prev => ({
      ...prev,
      skills: prev.skills?.filter(s => s !== skill) || []
    }))
  }

  const saveExperience = async (experience: Experience) => {
    try {
      if (experience.id) {
        await profileAPI.updateExperience(experience.id, experience)
      } else {
        await profileAPI.createExperience(experience)
      }
      
      setEditingExperience(null)
      fetchExperiences()
      setSuccess('Experience saved successfully!')
    } catch (error) {
      setError('Failed to save experience')
      console.error('Error saving experience:', error)
    }
  }

  const deleteExperience = async (id: number) => {
    try {
      await profileAPI.deleteExperience(id)
      fetchExperiences()
      setSuccess('Experience deleted successfully!')
    } catch (error) {
      setError('Failed to delete experience')
      console.error('Error deleting experience:', error)
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">Loading profile...</div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Profile Management</h1>
          <p className="text-muted-foreground">
            Manage your professional profile, experience, and application templates
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

        <Tabs defaultValue="profile" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="profile">Profile</TabsTrigger>
            <TabsTrigger value="experience">Experience</TabsTrigger>
            <TabsTrigger value="education">Education</TabsTrigger>
            <TabsTrigger value="templates">Templates</TabsTrigger>
          </TabsList>

          <TabsContent value="profile">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Personal Information
                </CardTitle>
                <CardDescription>
                  Update your basic profile information and preferences
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone</Label>
                    <Input
                      id="phone"
                      type="tel"
                      value={profile.phone || ''}
                      onChange={(e) => setProfile(prev => ({ ...prev, phone: e.target.value }))}
                      placeholder="+1 (555) 123-4567"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="location">Location</Label>
                    <Input
                      id="location"
                      value={profile.location || ''}
                      onChange={(e) => setProfile(prev => ({ ...prev, location: e.target.value }))}
                      placeholder="City, State"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="bio">Professional Bio</Label>
                  <Textarea
                    id="bio"
                    value={profile.bio || ''}
                    onChange={(e) => setProfile(prev => ({ ...prev, bio: e.target.value }))}
                    placeholder="Tell us about your professional background..."
                    rows={4}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Skills</Label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {profile.skills?.map((skill, index) => (
                      <Badge key={index} variant="secondary" className="flex items-center gap-1">
                        {skill}
                        <button
                          onClick={() => removeSkill(skill)}
                          className="ml-1 text-xs hover:text-red-500"
                        >
                          ×
                        </button>
                      </Badge>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <Input
                      value={newSkill}
                      onChange={(e) => setNewSkill(e.target.value)}
                      placeholder="Add a skill"
                      onKeyPress={(e) => e.key === 'Enter' && addSkill()}
                    />
                    <Button onClick={addSkill} size="sm">
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="experience_years">Years of Experience</Label>
                    <Input
                      id="experience_years"
                      type="number"
                      value={profile.experience_years || ''}
                      onChange={(e) => setProfile(prev => ({ ...prev, experience_years: parseInt(e.target.value) }))}
                      placeholder="5"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="availability">Availability</Label>
                    <Select
                      value={profile.availability || undefined}
                      onValueChange={(value) => setProfile(prev => ({ ...prev, availability: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select availability" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="immediately">Immediately</SelectItem>
                        <SelectItem value="2_weeks">2 weeks notice</SelectItem>
                        <SelectItem value="1_month">1 month notice</SelectItem>
                        <SelectItem value="3_months">3 months notice</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="salary_min">Minimum Salary ($)</Label>
                    <Input
                      id="salary_min"
                      type="number"
                      value={profile.preferred_salary_min || ''}
                      onChange={(e) => setProfile(prev => ({ ...prev, preferred_salary_min: parseInt(e.target.value) }))}
                      placeholder="50000"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="salary_max">Maximum Salary ($)</Label>
                    <Input
                      id="salary_max"
                      type="number"
                      value={profile.preferred_salary_max || ''}
                      onChange={(e) => setProfile(prev => ({ ...prev, preferred_salary_max: e.target.value }))}
                      placeholder="80000"
                    />
                  </div>
                </div>

                <Button onClick={saveProfile} disabled={saving} className="w-full">
                  <Save className="h-4 w-4 mr-2" />
                  {saving ? 'Saving...' : 'Save Profile'}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="experience">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Building className="h-5 w-5" />
                    Work Experience
                  </div>
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button onClick={() => setEditingExperience({
                        company: '',
                        position: '',
                        start_date: '',
                        end_date: '',
                        description: '',
                        is_current: false
                      })}>
                        <Plus className="h-4 w-4 mr-2" />
                        Add Experience
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-2xl">
                      <DialogHeader>
                        <DialogTitle>
                          {editingExperience?.id ? 'Edit Experience' : 'Add Experience'}
                        </DialogTitle>
                        <DialogDescription>
                          Add your work experience details
                        </DialogDescription>
                      </DialogHeader>
                      {editingExperience && (
                        <div className="space-y-4">
                          <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <Label>Company</Label>
                              <Input
                                value={editingExperience.company}
                                onChange={(e) => setEditingExperience(prev => prev ? { ...prev, company: e.target.value } : null)}
                                placeholder="Company name"
                              />
                            </div>
                            <div className="space-y-2">
                              <Label>Position</Label>
                              <Input
                                value={editingExperience.position}
                                onChange={(e) => setEditingExperience(prev => prev ? { ...prev, position: e.target.value } : null)}
                                placeholder="Job title"
                              />
                            </div>
                          </div>
                          <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <Label>Start Date</Label>
                              <Input
                                type="date"
                                value={editingExperience.start_date}
                                onChange={(e) => setEditingExperience(prev => prev ? { ...prev, start_date: e.target.value } : null)}
                              />
                            </div>
                            <div className="space-y-2">
                              <Label>End Date</Label>
                              <Input
                                type="date"
                                value={editingExperience.end_date || ''}
                                onChange={(e) => setEditingExperience(prev => prev ? { ...prev, end_date: e.target.value } : null)}
                                disabled={editingExperience.is_current}
                              />
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              id="current"
                              checked={editingExperience.is_current}
                              onChange={(e) => setEditingExperience(prev => prev ? { ...prev, is_current: e.target.checked, end_date: e.target.checked ? '' : prev.end_date } : null)}
                            />
                            <Label htmlFor="current">Currently working here</Label>
                          </div>
                          <div className="space-y-2">
                            <Label>Description</Label>
                            <Textarea
                              value={editingExperience.description || ''}
                              onChange={(e) => setEditingExperience(prev => prev ? { ...prev, description: e.target.value } : null)}
                              placeholder="Describe your role and achievements..."
                              rows={4}
                            />
                          </div>
                          <div className="flex gap-2">
                            <Button onClick={() => saveExperience(editingExperience)}>
                              <Save className="h-4 w-4 mr-2" />
                              Save Experience
                            </Button>
                            <Button variant="outline" onClick={() => setEditingExperience(null)}>
                              Cancel
                            </Button>
                          </div>
                        </div>
                      )}
                    </DialogContent>
                  </Dialog>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {experiences.map((exp) => (
                    <div key={exp.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold">{exp.position}</h3>
                          <p className="text-muted-foreground">{exp.company}</p>
                          <p className="text-sm text-muted-foreground">
                            {exp.start_date} - {exp.is_current ? 'Present' : exp.end_date}
                          </p>
                          {exp.description && (
                            <p className="mt-2 text-sm">{exp.description}</p>
                          )}
                        </div>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setEditingExperience(exp)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => exp.id && deleteExperience(exp.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                  {experiences.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      No work experience added yet. Click "Add Experience" to get started.
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="education">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <GraduationCap className="h-5 w-5" />
                  Education
                </CardTitle>
                <CardDescription>
                  Add your educational background
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-muted-foreground">
                  Education management coming soon...
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="templates">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Application Templates
                </CardTitle>
                <CardDescription>
                  Create and manage cover letter templates for different types of applications
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-muted-foreground">
                  Template management coming soon...
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
