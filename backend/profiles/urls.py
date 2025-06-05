from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('me/', views.ProfileDetailView.as_view(), name='profile-detail'),
    path('experience/', views.ExperienceListCreateView.as_view(), name='experience-list'),
    path('experience/<int:pk>/', views.ExperienceDetailView.as_view(), name='experience-detail'),
    path('education/', views.EducationListCreateView.as_view(), name='education-list'),
    path('education/<int:pk>/', views.EducationDetailView.as_view(), name='education-detail'),
    path('templates/', views.ApplicationTemplateListCreateView.as_view(), name='template-list'),
    path('templates/<int:pk>/', views.ApplicationTemplateDetailView.as_view(), name='template-detail'),
    path('upload-resume/', views.ResumeUploadView.as_view(), name='upload-resume'),
]
