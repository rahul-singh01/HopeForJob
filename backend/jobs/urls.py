from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'listings', views.JobListingViewSet, basename='joblisting')
router.register(r'sources', views.JobSourceViewSet, basename='jobsource')
router.register(r'saved', views.SavedJobViewSet, basename='savedjob')
router.register(r'alerts', views.JobAlertViewSet, basename='jobalert')
router.register(r'matches', views.JobMatchViewSet, basename='jobmatch')

urlpatterns = [
    path('', include(router.urls)),
    path('search/', views.JobSearchView.as_view(), name='job-search'),
    path('scrape/', views.JobScrapingView.as_view(), name='job-scrape'),
    path('recommendations/', views.JobRecommendationsView.as_view(), name='job-recommendations'),
    path('analytics/', views.JobAnalyticsView.as_view(), name='job-analytics'),
]
