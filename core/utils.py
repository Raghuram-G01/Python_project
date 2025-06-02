"""Utility functions for the blog application."""

import re
from django.utils.text import slugify
from django.utils.html import strip_tags
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def create_unique_slug(model_class, title, slug_field='slug'):
    """Create a unique slug for a model instance."""
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    
    while model_class.objects.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug


def extract_excerpt(content, max_length=200):
    """Extract excerpt from content."""
    # Strip HTML tags
    text = strip_tags(content)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    if len(text) <= max_length:
        return text
    
    # Find the last complete word within the limit
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return truncated + '...'


def paginate_queryset(queryset, page_number, per_page=10):
    """Paginate a queryset."""
    paginator = Paginator(queryset, per_page)
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    return page_obj


def calculate_reading_time(content):
    """Calculate estimated reading time for content."""
    # Strip HTML tags and count words
    text = strip_tags(content)
    word_count = len(text.split())
    
    # Average reading speed is 200-250 words per minute
    # We'll use 200 for a conservative estimate
    reading_time = max(1, round(word_count / 200))
    
    return reading_time


def generate_meta_description(content, max_length=160):
    """Generate meta description from content."""
    return extract_excerpt(content, max_length)


def clean_search_query(query):
    """Clean and validate search query."""
    if not query:
        return ''
    
    # Remove extra whitespace and special characters
    query = re.sub(r'[^\w\s-]', '', query)
    query = re.sub(r'\s+', ' ', query).strip()
    
    return query[:100]  # Limit query length


def format_file_size(size_bytes):
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def validate_image_file(file):
    """Validate uploaded image file."""
    if not file:
        return False
    
    # Check file size (max 5MB)
    if file.size > 5 * 1024 * 1024:
        return False
    
    # Check file extension
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    file_extension = file.name.lower().split('.')[-1]
    
    if f'.{file_extension}' not in allowed_extensions:
        return False
    
    return True
