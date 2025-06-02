"""Blog models for the blog application."""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MinLengthValidator
from taggit.managers import TaggableManager
from ckeditor_uploader.fields import RichTextUploadingField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
import uuid

from core.models import TimeStampedModel
from core.utils import create_unique_slug, extract_excerpt, calculate_reading_time


class Category(models.Model):
    """Blog category model."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(
        blank=True, help_text="Category description")
    color = models.CharField(
        max_length=7, default="#6366f1", help_text="Hex color code")
    icon = models.CharField(max_length=50, blank=True,
                            help_text="Font Awesome icon class")
    is_featured = models.BooleanField(
        default=False, help_text="Show in featured categories")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:category_posts', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = create_unique_slug(Category, self.name)
        super().save(*args, **kwargs)


class BlogPost(TimeStampedModel):
    """Main blog post model."""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    # Basic fields
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(5)],
        help_text="Post title (minimum 5 characters)"
    )
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='blogpost_set')

    # Content fields
    content = RichTextUploadingField(
        help_text="Post content with rich text editor")
    excerpt = models.TextField(
        max_length=500,
        blank=True,
        help_text="Brief description (auto-generated if empty)"
    )

    # Featured image
    featured_image = models.ImageField(
        upload_to='posts/images/',
        blank=True,
        null=True,
        help_text="Featured image for the post"
    )
    featured_image_thumbnail = ImageSpecField(
        source='featured_image',
        processors=[ResizeToFill(400, 250)],
        format='JPEG',
        options={'quality': 90}
    )
    featured_image_alt = models.CharField(
        max_length=200,
        blank=True,
        help_text="Alt text for featured image"
    )

    # Categorization
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Post category"
    )
    tags = TaggableManager(blank=True, help_text="Tags for the post")

    # Status and timestamps
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Post status"
    )
    published_at = models.DateTimeField(null=True, blank=True)

    # SEO fields
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Meta description for SEO (auto-generated if empty)"
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text="Meta keywords for SEO"
    )

    # Engagement metrics
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)

    # Additional fields
    reading_time = models.PositiveIntegerField(
        default=1,
        help_text="Estimated reading time in minutes"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Show in featured posts"
    )
    allow_comments = models.BooleanField(
        default=True,
        help_text="Allow comments on this post"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['author', 'status']),
            models.Index(fields=['category']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug:
            self.slug = create_unique_slug(BlogPost, self.title)

        # Auto-generate excerpt if not provided
        if not self.excerpt and self.content:
            self.excerpt = extract_excerpt(self.content)

        # Auto-generate meta description if not provided
        if not self.meta_description and self.excerpt:
            self.meta_description = self.excerpt[:160]

        # Calculate reading time
        if self.content:
            self.reading_time = calculate_reading_time(self.content)

        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        elif self.status != 'published':
            self.published_at = None

        super().save(*args, **kwargs)

    @property
    def comment_count(self):
        """Get approved comment count."""
        return self.comments.filter(is_approved=True).count()

    @property
    def is_published(self):
        """Check if post is published."""
        return self.status == 'published'

    def get_related_posts(self, limit=4):
        """Get related posts based on category and tags."""
        related = BlogPost.objects.filter(
            status='published'
        ).exclude(id=self.id)

        if self.category:
            related = related.filter(category=self.category)

        return related.order_by('-published_at')[:limit]


class PostLike(TimeStampedModel):
    """Track user likes for posts."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='post_likes')
    post = models.ForeignKey(
        BlogPost, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        unique_together = ('user', 'post')
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['post']),
        ]

    def __str__(self):
        return f'{self.user.username} likes {self.post.title}'


class PostBookmark(TimeStampedModel):
    """Track user bookmarks for posts."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='bookmarks')
    post = models.ForeignKey(
        BlogPost, on_delete=models.CASCADE, related_name='bookmarks')

    class Meta:
        unique_together = ('user', 'post')
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['post']),
        ]

    def __str__(self):
        return f'{self.user.username} bookmarked {self.post.title}'


class PostView(models.Model):
    """Track post views for analytics."""

    post = models.ForeignKey(
        BlogPost, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['ip_address']),
        ]

    def __str__(self):
        return f'View of {self.post.title} at {self.created_at}'
