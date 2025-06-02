"""Admin configuration for core app."""

from django.contrib import admin
from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Site settings admin configuration."""
    
    list_display = ['site_name', 'contact_email', 'allow_comments', 'allow_registration']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('site_name', 'site_description', 'site_logo', 'site_favicon')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'contact_address')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url', 'github_url'),
            'classes': ('collapse',)
        }),
        ('SEO Settings', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Analytics', {
            'fields': ('google_analytics_id', 'google_search_console_id'),
            'classes': ('collapse',)
        }),
        ('Features', {
            'fields': ('allow_comments', 'moderate_comments', 'allow_registration')
        }),
    )
    
    def has_add_permission(self, request):
        """Only allow one instance of site settings."""
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Don't allow deletion of site settings."""
        return False
