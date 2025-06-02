"""URL configuration for AI features."""

from django.urls import path
from . import views

app_name = 'ai_features'

urlpatterns = [
    # AI Content Generation
    path('generate/', views.content_generator_view, name='content_generator'),
    path('api/generate/', views.generate_content_api, name='generate_content_api'),
    
    # Content Summarization
    path('api/summarize/', views.summarize_api, name='summarize_api'),
    
    # SEO Analysis
    path('seo-analyzer/', views.seo_analyzer_view, name='seo_analyzer'),
    path('api/seo-analyze/', views.seo_analyze_api, name='seo_analyze_api'),
    
    # Content Moderation
    path('api/moderate/', views.moderate_content_api, name='moderate_content_api'),
    
    # Chatbot
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    
    # AI Tasks Management
    path('tasks/', views.ai_tasks_view, name='ai_tasks'),
    path('api/tasks/<uuid:task_id>/', views.ai_task_status_api, name='ai_task_status'),
    
    # Content Templates
    path('templates/', views.content_templates_view, name='content_templates'),
    path('api/templates/', views.content_templates_api, name='content_templates_api'),
]
