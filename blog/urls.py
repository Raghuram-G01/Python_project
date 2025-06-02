"""URL configuration for the blog app."""

from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Main blog views
    path('', views.home, name='home'),
    path('posts/', views.post_list, name='post_list'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),

    # Post management
    path('create/', views.create_post, name='create_post'),
    path('post/<slug:slug>/edit/', views.edit_post, name='edit_post'),
    path('post/<slug:slug>/delete/', views.delete_post, name='delete_post'),

    # Category and tag views
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
    path('tag/<slug:tag_slug>/', views.tag_posts, name='tag_posts'),
    path('categories/', views.category_list, name='category_list'),

    # Search and filtering
    path('search/', views.search_posts, name='search_posts'),

    # Post interactions (AJAX)
    path('api/like-post/<slug:slug>/', views.like_post, name='like_post'),
    path('api/bookmark-post/<slug:slug>/',
         views.bookmark_post, name='bookmark_post'),
    path('api/track-view/<slug:slug>/', views.track_view, name='track_view'),

    # Sitemap and feeds
    path('sitemap.xml', views.sitemap, name='sitemap'),
    path('feed/', views.rss_feed, name='rss_feed'),
]
