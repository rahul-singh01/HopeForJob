from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('activities/', views.UserActivityListView.as_view(), name='user-activities'),
    path('api-keys/', views.APIKeyListCreateView.as_view(), name='api-keys'),
    path('api-keys/<uuid:key>/', views.APIKeyDetailView.as_view(), name='api-key-detail'),
]
