"""Blog views for the blog application."""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, Count, F
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from taggit.models import Tag
import json
import logging

from .models import BlogPost, Category, PostLike, PostBookmark, PostView
from .forms import BlogPostForm, SearchForm
from core.utils import get_client_ip, paginate_queryset
from users.models import UserProfile

logger = logging.getLogger(__name__)


def home(request):
    """Home page with featured and recent content."""
    # Get featured posts
    featured_posts = BlogPost.objects.filter(
        status='published',
        is_featured=True
    ).order_by('-published_at')[:6]

    # If no featured posts, get recent posts
    if not featured_posts:
        featured_posts = BlogPost.objects.filter(
            status='published'
        ).order_by('-published_at')[:6]

    # Get popular posts
    popular_posts = BlogPost.objects.filter(
        status='published'
    ).order_by('-view_count', '-like_count')[:4]

    # Get recent posts
    recent_posts = BlogPost.objects.filter(
        status='published'
    ).order_by('-published_at')[:8]

    # Get featured categories
    featured_categories = Category.objects.filter(
        is_featured=True
    ).annotate(
        post_count=Count('blogpost', filter=Q(blogpost__status='published'))
    ).filter(post_count__gt=0)[:6]

    context = {
        'featured_posts': featured_posts,
        'popular_posts': popular_posts,
        'recent_posts': recent_posts,
        'featured_categories': featured_categories,
    }

    return render(request, 'blog/home.html', context)


def post_list(request):
    """List all published posts with filtering and search."""
    form = SearchForm(request.GET)
    posts = BlogPost.objects.filter(status='published')

    # Apply filters from search form
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        tag = form.cleaned_data.get('tag')
        sort_by = form.cleaned_data.get('sort_by', '-published_at')

        # Text search
        if query:
            posts = posts.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query)
            )

        # Category filter
        if category:
            posts = posts.filter(category=category)

        # Tag filter
        if tag:
            posts = posts.filter(tags__name__icontains=tag)

        # Sorting
        if sort_by:
            posts = posts.order_by(sort_by)
    else:
        posts = posts.order_by('-published_at')

    # Pagination
    page_obj = paginate_queryset(posts, request.GET.get(
        'page'), getattr(settings, 'BLOG_POSTS_PER_PAGE', 12))

    # Get categories and popular tags for sidebar
    categories = Category.objects.annotate(
        post_count=Count('blogpost', filter=Q(blogpost__status='published'))
    ).filter(post_count__gt=0).order_by('-post_count')

    popular_tags = Tag.objects.annotate(
        post_count=Count('taggit_taggeditem_items',
                         filter=Q(taggit_taggeditem_items__content_type__model='blogpost'))
    ).filter(post_count__gt=0).order_by('-post_count')[:20]

    context = {
        'form': form,
        'page_obj': page_obj,
        'categories': categories,
        'popular_tags': popular_tags,
    }

    return render(request, 'blog/post_list.html', context)


def post_detail(request, slug):
    """Display individual post with comments and interactions."""
    post = get_object_or_404(BlogPost, slug=slug, status='published')

    # Track view (will be handled by AJAX for better performance)
    # But increment view count for now
    post.view_count = F('view_count') + 1
    post.save(update_fields=['view_count'])
    post.refresh_from_db()

    # Get related posts
    related_posts = post.get_related_posts()

    # Get approved comments (will be handled by comments app)
    comments = post.comments.filter(is_approved=True).order_by('created_at')

    # Check user interactions
    user_liked = False
    user_bookmarked = False
    if request.user.is_authenticated:
        user_liked = PostLike.objects.filter(
            user=request.user, post=post).exists()
        user_bookmarked = PostBookmark.objects.filter(
            user=request.user, post=post).exists()

    context = {
        'post': post,
        'related_posts': related_posts,
        'comments': comments,
        'user_liked': user_liked,
        'user_bookmarked': user_bookmarked,
    }

    return render(request, 'blog/post_detail.html', context)


@login_required
def create_post(request):
    """Create a new blog post."""
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()  # Save many-to-many relationships

            if post.status == 'published':
                messages.success(request, 'Post published successfully!')
            else:
                messages.success(request, 'Post saved as draft!')

            return redirect('blog:post_detail', slug=post.slug)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BlogPostForm()

    context = {
        'form': form,
        'title': 'Create New Post',
    }

    return render(request, 'blog/post_form.html', context)


@login_required
def edit_post(request, slug):
    """Edit an existing blog post."""
    post = get_object_or_404(BlogPost, slug=slug)

    # Check if user can edit this post
    if post.author != request.user and not request.user.is_staff:
        raise PermissionDenied("You can only edit your own posts.")

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()

            if post.status == 'published':
                messages.success(
                    request, 'Post updated and published successfully!')
            else:
                messages.success(request, 'Post updated and saved as draft!')

            return redirect('blog:post_detail', slug=post.slug)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BlogPostForm(instance=post)

    context = {
        'form': form,
        'post': post,
        'title': f'Edit: {post.title}',
    }

    return render(request, 'blog/post_form.html', context)


@login_required
def delete_post(request, slug):
    """Delete a blog post."""
    post = get_object_or_404(BlogPost, slug=slug)

    # Check if user can delete this post
    if post.author != request.user and not request.user.is_staff:
        raise PermissionDenied("You can only delete your own posts.")

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('blog:post_list')

    context = {
        'post': post,
    }

    return render(request, 'blog/delete_post.html', context)


# Category and Tag Views

def category_posts(request, slug):
    """Display posts from a specific category."""
    category = get_object_or_404(Category, slug=slug)
    posts = BlogPost.objects.filter(
        status='published',
        category=category
    ).order_by('-published_at')

    # Pagination
    page_obj = paginate_queryset(posts, request.GET.get(
        'page'), getattr(settings, 'BLOG_POSTS_PER_PAGE', 12))

    context = {
        'category': category,
        'page_obj': page_obj,
    }

    return render(request, 'blog/category_posts.html', context)


def tag_posts(request, tag_slug):
    """Display posts with a specific tag."""
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = BlogPost.objects.filter(
        status='published',
        tags=tag
    ).order_by('-published_at')

    # Pagination
    page_obj = paginate_queryset(posts, request.GET.get(
        'page'), getattr(settings, 'BLOG_POSTS_PER_PAGE', 12))

    context = {
        'tag': tag,
        'page_obj': page_obj,
    }

    return render(request, 'blog/tag_posts.html', context)


def category_list(request):
    """Display all categories."""
    categories = Category.objects.annotate(
        post_count=Count('blogpost', filter=Q(blogpost__status='published'))
    ).filter(post_count__gt=0).order_by('name')

    context = {
        'categories': categories,
    }

    return render(request, 'blog/category_list.html', context)


def search_posts(request):
    """Search posts."""
    form = SearchForm(request.GET)
    posts = BlogPost.objects.filter(status='published')
    query = None

    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        tag = form.cleaned_data.get('tag')
        sort_by = form.cleaned_data.get('sort_by', '-published_at')

        # Text search
        if query:
            posts = posts.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query)
            )

        # Category filter
        if category:
            posts = posts.filter(category=category)

        # Tag filter
        if tag:
            posts = posts.filter(tags__name__icontains=tag)

        # Sorting
        if sort_by:
            posts = posts.order_by(sort_by)
    else:
        posts = posts.order_by('-published_at')

    # Pagination
    page_obj = paginate_queryset(posts, request.GET.get(
        'page'), getattr(settings, 'BLOG_POSTS_PER_PAGE', 12))

    context = {
        'form': form,
        'page_obj': page_obj,
        'query': query,
    }

    return render(request, 'blog/search_results.html', context)


# AJAX Views for Post Interactions

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def like_post(request, slug):
    """Like or unlike a post."""
    post = get_object_or_404(BlogPost, slug=slug, status='published')

    try:
        like = PostLike.objects.get(user=request.user, post=post)
        like.delete()
        liked = False
        message = 'Post unliked'
    except PostLike.DoesNotExist:
        PostLike.objects.create(user=request.user, post=post)
        liked = True
        message = 'Post liked'

    # Update post like count
    like_count = post.likes.count()
    post.like_count = like_count
    post.save(update_fields=['like_count'])

    return JsonResponse({
        'success': True,
        'liked': liked,
        'like_count': like_count,
        'message': message
    })


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def bookmark_post(request, slug):
    """Bookmark or unbookmark a post."""
    post = get_object_or_404(BlogPost, slug=slug, status='published')

    try:
        bookmark = PostBookmark.objects.get(user=request.user, post=post)
        bookmark.delete()
        bookmarked = False
        message = 'Bookmark removed'
    except PostBookmark.DoesNotExist:
        PostBookmark.objects.create(user=request.user, post=post)
        bookmarked = True
        message = 'Post bookmarked'

    return JsonResponse({
        'success': True,
        'bookmarked': bookmarked,
        'message': message
    })


@csrf_exempt
@require_http_methods(["POST"])
def track_view(request, slug):
    """Track post view for analytics."""
    post = get_object_or_404(BlogPost, slug=slug, status='published')

    # Create view record
    PostView.objects.create(
        post=post,
        user=request.user if request.user.is_authenticated else None,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        referrer=request.META.get('HTTP_REFERER', '')
    )

    return JsonResponse({'success': True})


# Utility Views

def sitemap(request):
    """Generate XML sitemap."""
    posts = BlogPost.objects.filter(
        status='published').order_by('-published_at')
    categories = Category.objects.all()

    context = {
        'posts': posts,
        'categories': categories,
        'domain': request.get_host(),
    }

    return render(request, 'blog/sitemap.xml', context, content_type='application/xml')


def rss_feed(request):
    """Generate RSS feed."""
    posts = BlogPost.objects.filter(
        status='published').order_by('-published_at')[:20]

    context = {
        'posts': posts,
        'domain': request.get_host(),
        'site_name': 'Blog Spot',
        'site_description': 'A modern blog platform',
    }

    return render(request, 'blog/rss_feed.xml', context, content_type='application/rss+xml')


# Helper Functions (Non-AI)

def get_popular_posts(limit=6):
    """Get popular posts based on views and likes."""
    return BlogPost.objects.filter(
        status='published'
    ).order_by('-view_count', '-like_count')[:limit]


def get_recent_posts(limit=6):
    """Get recent published posts."""
    return BlogPost.objects.filter(
        status='published'
    ).order_by('-published_at')[:limit]
