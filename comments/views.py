"""Views for the comments app."""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
import json

from .models import Comment, CommentLike, CommentFlag
from .forms import CommentForm, CommentFlagForm
from blog.models import BlogPost


@login_required
@require_http_methods(["POST"])
def add_comment(request, post_slug):
    """Add a new comment to a blog post."""
    post = get_object_or_404(BlogPost, slug=post_slug, status='published')
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            
            # Handle parent comment for replies
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    parent_comment = Comment.objects.get(id=parent_id, post=post)
                    comment.parent = parent_comment
                except Comment.DoesNotExist:
                    pass
            
            comment.save()
            messages.success(request, 'Your comment has been added successfully!')
            
            # Return JSON response for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Comment added successfully!',
                    'comment_id': comment.id,
                    'comment_html': render_comment_html(comment, request)
                })
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
            messages.error(request, 'Please correct the errors in your comment.')
    
    return redirect('blog:post_detail', slug=post_slug)


@login_required
def edit_comment(request, comment_id):
    """Edit an existing comment."""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Check if user can edit this comment
    if comment.author != request.user:
        raise PermissionDenied("You can only edit your own comments.")
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your comment has been updated successfully!')
            return redirect('blog:post_detail', slug=comment.post.slug)
        else:
            messages.error(request, 'Please correct the errors in your comment.')
    else:
        form = CommentForm(instance=comment)
    
    context = {
        'form': form,
        'comment': comment,
        'post': comment.post,
    }
    return render(request, 'comments/edit_comment.html', context)


@login_required
def delete_comment(request, comment_id):
    """Delete a comment."""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Check if user can delete this comment
    if comment.author != request.user and not request.user.is_staff:
        raise PermissionDenied("You can only delete your own comments.")
    
    if request.method == 'POST':
        post_slug = comment.post.slug
        comment.delete()
        messages.success(request, 'Comment has been deleted successfully!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Comment deleted successfully!'})
        
        return redirect('blog:post_detail', slug=post_slug)
    
    context = {
        'comment': comment,
        'post': comment.post,
    }
    return render(request, 'comments/delete_comment.html', context)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def like_comment(request, comment_id):
    """Like or unlike a comment."""
    comment = get_object_or_404(Comment, id=comment_id)
    
    try:
        like = CommentLike.objects.get(comment=comment, user=request.user)
        like.delete()
        liked = False
        message = 'Comment unliked'
    except CommentLike.DoesNotExist:
        CommentLike.objects.create(comment=comment, user=request.user)
        liked = True
        message = 'Comment liked'
    
    like_count = comment.likes.count()
    
    return JsonResponse({
        'success': True,
        'liked': liked,
        'like_count': like_count,
        'message': message
    })


@login_required
def flag_comment(request, comment_id):
    """Flag a comment as inappropriate."""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Check if user has already flagged this comment
    if CommentFlag.objects.filter(comment=comment, user=request.user).exists():
        messages.warning(request, 'You have already flagged this comment.')
        return redirect('blog:post_detail', slug=comment.post.slug)
    
    if request.method == 'POST':
        form = CommentFlagForm(request.POST)
        if form.is_valid():
            flag = form.save(commit=False)
            flag.comment = comment
            flag.user = request.user
            flag.save()
            
            # Mark comment as flagged if it receives multiple flags
            flag_count = comment.flags.count()
            if flag_count >= 3:  # Threshold for auto-flagging
                comment.is_flagged = True
                comment.save()
            
            messages.success(request, 'Thank you for reporting this comment. We will review it shortly.')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Comment flagged successfully!'
                })
            
            return redirect('blog:post_detail', slug=comment.post.slug)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
    else:
        form = CommentFlagForm()
    
    context = {
        'form': form,
        'comment': comment,
        'post': comment.post,
    }
    return render(request, 'comments/flag_comment.html', context)


def render_comment_html(comment, request):
    """Render comment HTML for AJAX responses."""
    from django.template.loader import render_to_string
    
    return render_to_string('comments/comment_item.html', {
        'comment': comment,
        'user': request.user,
    }, request=request)
