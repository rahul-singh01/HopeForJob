from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sessions', views.AutomationSessionViewSet, basename='automationsession')
router.register(r'applications', views.JobApplicationViewSet, basename='jobapplication')
router.register(r'rules', views.AutomationRuleViewSet, basename='automationrule')
router.register(r'credentials', views.PlatformCredentialsViewSet, basename='platformcredentials')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', views.AutomationStatsView.as_view(), name='automation-stats'),
    path('bulk-apply/', views.BulkApplyView.as_view(), name='bulk-apply'),
]
