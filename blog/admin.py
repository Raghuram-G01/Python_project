"""Admin configuration for blog app."""

from django.contrib import admin
from django.utils.html import format_html

from .models import Category, BlogPost, PostLike, PostBookmark, PostView


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category admin configuration."""

    list_display = ['name', 'slug', 'post_count', 'is_featured', 'created_at']
    list_filter = ['is_featured', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Appearance', {
            'fields': ('color', 'icon', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def post_count(self, obj):
        return obj.post_count
    post_count.short_description = 'Published Posts'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """Blog post admin configuration."""

    list_display = [
        'title', 'author', 'status', 'category', 'is_featured',
        'published_at', 'view_count', 'like_count', 'reading_time'
    ]
    list_filter = [
        'status', 'is_featured', 'allow_comments', 'category',
        'created_at', 'published_at'
    ]
    search_fields = ['title', 'content', 'excerpt', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    readonly_fields = [
        'view_count', 'like_count', 'reading_time',
        'created_at', 'updated_at'
    ]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'content', 'excerpt')
        }),
        ('Media', {
            'fields': ('featured_image', 'featured_image_alt')
        }),
        ('Categorization', {
            'fields': ('category', 'tags')
        }),
        ('Publishing Options', {
            'fields': ('status', 'is_featured', 'allow_comments')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Analytics', {
            'fields': ('view_count', 'like_count', 'reading_time'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        })
    )

    actions = ['make_published', 'make_draft', 'make_featured']

    def make_published(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated} posts were published.')
    make_published.short_description = "Publish selected posts"

    def make_draft(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} posts were moved to draft.')
    make_draft.short_description = "Move selected posts to draft"

    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} posts were marked as featured.')
    make_featured.short_description = "Mark selected posts as featured"


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    """Post like admin configuration."""

    list_display = ['user', 'post_title', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'post__title']
    readonly_fields = ['created_at', 'updated_at']

    def post_title(self, obj):
        return obj.post.title
    post_title.short_description = 'Post'


@admin.register(PostBookmark)
class PostBookmarkAdmin(admin.ModelAdmin):
    """Post bookmark admin configuration."""

    list_display = ['user', 'post_title', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'post__title']
    readonly_fields = ['created_at', 'updated_at']

    def post_title(self, obj):
        return obj.post.title
    post_title.short_description = 'Post'


@admin.register(PostView)
class PostViewAdmin(admin.ModelAdmin):
    """Post view admin configuration."""

    list_display = ['post_title', 'user', 'ip_address', 'created_at']
    list_filter = ['created_at']
    search_fields = ['post__title', 'user__username', 'ip_address']
    readonly_fields = ['created_at']

    def post_title(self, obj):
        return obj.post.title
    post_title.short_description = 'Post'
