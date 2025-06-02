"""AI Features models for the blog application."""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class AITask(models.Model):
    """Track AI processing tasks"""
    TASK_TYPES = [
        ('content_generation', 'Content Generation'),
        ('summarization', 'Summarization'),
        ('seo_optimization', 'SEO Optimization'),
        ('sentiment_analysis', 'Sentiment Analysis'),
        ('moderation', 'Content Moderation'),
        ('embedding_generation', 'Embedding Generation'),
        ('personalization', 'Personalization'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_type = models.CharField(max_length=50, choices=TASK_TYPES)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')

    # Task details
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)

    # Metadata
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    processing_time = models.FloatField(
        null=True, blank=True, help_text="Time in seconds")

    # AI model info
    model_used = models.CharField(max_length=100, blank=True)
    api_cost = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task_type', 'status']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f'{self.task_type} - {self.status}'


class ContentTemplate(models.Model):
    """AI content generation templates"""
    TEMPLATE_TYPES = [
        ('blog_post', 'Blog Post'),
        ('tutorial', 'Tutorial'),
        ('review', 'Review'),
        ('news', 'News Article'),
        ('opinion', 'Opinion Piece'),
        ('listicle', 'Listicle'),
    ]

    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    description = models.TextField()

    # Template structure
    prompt_template = models.TextField(
        help_text="AI prompt template with placeholders")
    structure_guidelines = models.JSONField(default=dict)
    tone_settings = models.JSONField(default=dict)

    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)
    success_rate = models.FloatField(default=0.0)

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.template_type})'


class SEOAnalysis(models.Model):
    """Store SEO analysis results"""
    blog_post = models.OneToOneField('blog.BlogPost', on_delete=models.CASCADE)

    # SEO scores
    overall_score = models.FloatField(default=0.0)
    keyword_density_score = models.FloatField(default=0.0)
    readability_score = models.FloatField(default=0.0)
    meta_optimization_score = models.FloatField(default=0.0)
    content_structure_score = models.FloatField(default=0.0)

    # Detailed analysis
    keyword_analysis = models.JSONField(default=dict)
    readability_metrics = models.JSONField(default=dict)
    content_suggestions = models.JSONField(default=list)
    meta_suggestions = models.JSONField(default=list)

    # Recommended improvements
    title_suggestions = models.JSONField(default=list)
    meta_description_suggestions = models.JSONField(default=list)
    keyword_suggestions = models.JSONField(default=list)

    # Analysis metadata
    analyzed_at = models.DateTimeField(auto_now=True)
    analysis_version = models.CharField(max_length=10, default='1.0')

    def __str__(self):
        return f'SEO Analysis for {self.blog_post.title}'


class ChatbotConversation(models.Model):
    """Store chatbot conversations"""
    session_id = models.UUIDField(default=uuid.uuid4, db_index=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)

    # Conversation data
    messages = models.JSONField(default=list)
    context = models.JSONField(default=dict)

    # Metadata
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # Analytics
    message_count = models.PositiveIntegerField(default=0)
    user_satisfaction = models.IntegerField(
        null=True, blank=True, help_text="1-5 rating")

    class Meta:
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['user', 'started_at']),
        ]

    def __str__(self):
        return f'Conversation {self.session_id}'
