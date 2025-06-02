"""Admin configuration for AI features models."""

from django.contrib import admin
from .models import AITask, ContentTemplate, SEOAnalysis, ChatbotConversation


@admin.register(AITask)
class AITaskAdmin(admin.ModelAdmin):
    list_display = ['task_type', 'status', 'user',
                    'model_used', 'created_at', 'processing_time']
    list_filter = ['task_type', 'status', 'created_at']
    search_fields = ['user__username', 'model_used']
    readonly_fields = ['id', 'created_at',
                       'started_at', 'completed_at', 'processing_time']

    fieldsets = (
        ('Task Information', {
            'fields': ('task_type', 'status', 'user', 'model_used')
        }),
        ('Data', {
            'fields': ('input_data', 'output_data', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': ('created_at', 'started_at', 'completed_at', 'processing_time'),
            'classes': ('collapse',)
        }),
        ('Cost', {
            'fields': ('api_cost',),
            'classes': ('collapse',)
        })
    )


@admin.register(ContentTemplate)
class ContentTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'created_by',
                    'usage_count', 'success_rate', 'is_active']
    list_filter = ['template_type', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'created_by__username']
    readonly_fields = ['usage_count',
                       'success_rate', 'created_at', 'updated_at']


@admin.register(SEOAnalysis)
class SEOAnalysisAdmin(admin.ModelAdmin):
    list_display = ['blog_post', 'overall_score', 'analyzed_at']
    list_filter = ['analyzed_at']
    search_fields = ['blog_post__title']
    readonly_fields = ['analyzed_at', 'analysis_version']


@admin.register(ChatbotConversation)
class ChatbotConversationAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'message_count',
                    'user_satisfaction', 'started_at', 'is_active']
    list_filter = ['is_active', 'user_satisfaction', 'started_at']
    search_fields = ['user__username', 'session_id']
    readonly_fields = ['session_id', 'started_at',
                       'last_activity', 'message_count']
