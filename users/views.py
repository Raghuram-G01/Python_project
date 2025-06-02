"""User views for the blog application."""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .models import UserProfile, Newsletter, ContactMessage
from .forms import (
    UserRegistrationForm, UserAccountForm, UserProfileForm,
    PasswordChangeForm, NewsletterForm, ContactForm
)
from blog.models import BlogPost


def register(request):
    """User registration view."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(
                request, f'Account created for {username}! You can now log in.')
            return redirect('users:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def profile_edit(request):
    """Edit user profile view with account and profile information."""
    profile = request.user.profile

    if request.method == 'POST':
        account_form = UserAccountForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=profile)

        # Handle avatar deletion
        if request.POST.get('delete_avatar') == 'true':
            if profile.avatar:
                profile.avatar.delete(save=False)
                profile.avatar = None

        if account_form.is_valid() and profile_form.is_valid():
            account_form.save()
            profile_instance = profile_form.save()

            # Handle avatar deletion after form save
            if request.POST.get('delete_avatar') == 'true':
                profile_instance.avatar = None
                profile_instance.save()

            messages.success(
                request, 'Your profile has been updated successfully!')
            return redirect('users:profile', username=request.user.username)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        account_form = UserAccountForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)

    context = {
        'account_form': account_form,
        'profile_form': profile_form,
    }
    return render(request, 'users/profile_edit.html', context)


@login_required
def change_password(request):
    """Change user password view."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            # Update session to prevent logout
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            messages.success(
                request, 'Your password has been changed successfully!')
            return redirect('users:profile', username=request.user.username)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'users/change_password.html', {'form': form})


def profile_view(request, username):
    """View user profile and their posts."""
    user = get_object_or_404(User, username=username)
    profile = user.profile

    # Get user's published posts
    posts = BlogPost.objects.filter(
        author=user,
        status='published'
    ).order_by('-published_at')

    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get post statistics
    post_stats = {
        'total_posts': posts.count(),
        'total_views': sum(post.view_count for post in posts),
        'total_likes': sum(post.like_count for post in posts),
    }

    context = {
        'profile_user': user,
        'profile': profile,
        'page_obj': page_obj,
        'post_stats': post_stats,
        'is_own_profile': request.user == user,
    }

    return render(request, 'users/profile.html', context)


def newsletter_subscribe(request):
    """Newsletter subscription view."""
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            name = form.cleaned_data.get('name', '')

            newsletter, created = Newsletter.objects.get_or_create(
                email=email,
                defaults={'name': name, 'is_active': True}
            )

            if created:
                messages.success(
                    request, 'Thank you for subscribing to our newsletter!')
            else:
                if newsletter.is_active:
                    messages.info(
                        request, 'You are already subscribed to our newsletter.')
                else:
                    newsletter.is_active = True
                    newsletter.save()
                    messages.success(
                        request, 'Welcome back! Your subscription has been reactivated.')

            return redirect('blog:home')
        else:
            messages.error(request, 'Please enter a valid email address.')

    return redirect('blog:home')


@csrf_exempt
@require_http_methods(["POST"])
def newsletter_subscribe_ajax(request):
    """AJAX newsletter subscription."""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        name = data.get('name', '').strip()

        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required.'})

        newsletter, created = Newsletter.objects.get_or_create(
            email=email,
            defaults={'name': name, 'is_active': True}
        )

        if created:
            return JsonResponse({
                'success': True,
                'message': 'Thank you for subscribing to our newsletter!'
            })
        else:
            if newsletter.is_active:
                return JsonResponse({
                    'success': False,
                    'message': 'You are already subscribed to our newsletter.'
                })
            else:
                newsletter.is_active = True
                newsletter.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Welcome back! Your subscription has been reactivated.'
                })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred. Please try again.'
        })


def contact(request):
    """Contact form view."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            messages.success(
                request, 'Thank you for your message! We will get back to you soon.')
            return redirect('users:contact')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()

    return render(request, 'users/contact.html', {'form': form})


def authors_list(request):
    """List all authors with their post counts."""
    authors = User.objects.filter(
        blogpost_set__status='published'
    ).annotate(
        post_count=Count('blogpost_set')
    ).order_by('-post_count')

    context = {
        'authors': authors,
    }
    return render(request, 'users/authors.html', context)
