"""Comment models for the blog application."""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class Comment(models.Model):
    """Comment model for blog posts."""
    
    post = models.ForeignKey('blog.BlogPost', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    content = models.TextField(help_text="Your comment")
    
    # Moderation
    is_approved = models.BooleanField(default=True, help_text="Comment is approved for display")
    is_flagged = models.BooleanField(default=False, help_text="Comment has been flagged for review")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'is_approved']),
            models.Index(fields=['author']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'
    
    def get_absolute_url(self):
        return f"{self.post.get_absolute_url()}#comment-{self.id}"
    
    @property
    def is_reply(self):
        return self.parent is not None
    
    @property
    def reply_count(self):
        return self.replies.filter(is_approved=True).count()
    
    def get_replies(self):
        return self.replies.filter(is_approved=True).order_by('created_at')


class CommentLike(models.Model):
    """Like model for comments."""
    
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Comment Like"
        verbose_name_plural = "Comment Likes"
        unique_together = ('comment', 'user')
        indexes = [
            models.Index(fields=['comment']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f'{self.user.username} likes comment by {self.comment.author.username}'


class CommentFlag(models.Model):
    """Flag model for inappropriate comments."""
    
    REASON_CHOICES = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('hate_speech', 'Hate Speech'),
        ('inappropriate', 'Inappropriate Content'),
        ('off_topic', 'Off Topic'),
        ('other', 'Other'),
    ]
    
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='flags')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_flags')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(blank=True, help_text="Additional details about the flag")
    
    # Status
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='resolved_flags'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Comment Flag"
        verbose_name_plural = "Comment Flags"
        unique_together = ('comment', 'user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Flag by {self.user.username} for {self.reason}'
    
    def resolve(self, resolved_by_user):
        """Mark flag as resolved."""
        self.is_resolved = True
        self.resolved_by = resolved_by_user
        self.resolved_at = timezone.now()
        self.save()
