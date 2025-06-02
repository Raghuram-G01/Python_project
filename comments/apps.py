"""Comments app configuration."""

from django.apps import AppConfig


class CommentsConfig(AppConfig):
    """Comments app configuration."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'comments'
