"""URL configuration for analytics."""

from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Analytics Dashboard
    path('', views.analytics_dashboard, name='dashboard'),
    path('posts/', views.post_analytics, name='post_analytics'),
    path('users/', views.user_analytics, name='user_analytics'),
    
    # API endpoints
    path('api/engagement/', views.engagement_data_api, name='engagement_data_api'),
    path('api/popular-posts/', views.popular_posts_api, name='popular_posts_api'),
    path('api/user-behavior/', views.user_behavior_api, name='user_behavior_api'),
    path('api/content-performance/', views.content_performance_api, name='content_performance_api'),
]
