"""Admin configuration for comments app."""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Comment, CommentLike, CommentFlag


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Comment admin."""
    list_display = ('author', 'post_title', 'content_preview', 'is_approved', 'is_flagged', 'created_at', 'reply_count')
    list_filter = ('is_approved', 'is_flagged', 'created_at', 'post__category')
    search_fields = ('author__username', 'content', 'post__title')
    readonly_fields = ('created_at', 'updated_at', 'reply_count')
    actions = ['approve_comments', 'unapprove_comments', 'flag_comments', 'unflag_comments']
    
    fieldsets = (
        ('Comment Details', {
            'fields': ('post', 'author', 'parent', 'content')
        }),
        ('Moderation', {
            'fields': ('is_approved', 'is_flagged')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def post_title(self, obj):
        return obj.post.title
    post_title.short_description = 'Post'
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'
    
    def reply_count(self, obj):
        return obj.replies.count()
    reply_count.short_description = 'Replies'
    
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} comments were approved.')
    approve_comments.short_description = "Approve selected comments"
    
    def unapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} comments were unapproved.')
    unapprove_comments.short_description = "Unapprove selected comments"
    
    def flag_comments(self, request, queryset):
        updated = queryset.update(is_flagged=True)
        self.message_user(request, f'{updated} comments were flagged.')
    flag_comments.short_description = "Flag selected comments"
    
    def unflag_comments(self, request, queryset):
        updated = queryset.update(is_flagged=False)
        self.message_user(request, f'{updated} comments were unflagged.')
    unflag_comments.short_description = "Unflag selected comments"


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    """Comment like admin."""
    list_display = ('user', 'comment_author', 'comment_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'comment__content', 'comment__author__username')
    readonly_fields = ('created_at',)
    
    def comment_author(self, obj):
        return obj.comment.author.username
    comment_author.short_description = 'Comment Author'
    
    def comment_preview(self, obj):
        return obj.comment.content[:50] + '...' if len(obj.comment.content) > 50 else obj.comment.content
    comment_preview.short_description = 'Comment'


@admin.register(CommentFlag)
class CommentFlagAdmin(admin.ModelAdmin):
    """Comment flag admin."""
    list_display = ('user', 'comment_author', 'reason', 'is_resolved', 'created_at')
    list_filter = ('reason', 'is_resolved', 'created_at')
    search_fields = ('user__username', 'comment__content', 'comment__author__username', 'description')
    readonly_fields = ('created_at', 'resolved_at')
    actions = ['resolve_flags', 'unresolve_flags']
    
    fieldsets = (
        ('Flag Details', {
            'fields': ('comment', 'user', 'reason', 'description')
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolved_by', 'resolved_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def comment_author(self, obj):
        return obj.comment.author.username
    comment_author.short_description = 'Comment Author'
    
    def resolve_flags(self, request, queryset):
        updated = 0
        for flag in queryset:
            if not flag.is_resolved:
                flag.resolve(request.user)
                updated += 1
        self.message_user(request, f'{updated} flags were resolved.')
    resolve_flags.short_description = "Resolve selected flags"
    
    def unresolve_flags(self, request, queryset):
        updated = queryset.update(is_resolved=False, resolved_by=None, resolved_at=None)
        self.message_user(request, f'{updated} flags were unresolved.')
    unresolve_flags.short_description = "Unresolve selected flags"
