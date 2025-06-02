"""URL configuration for comments app."""

from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    # Comment CRUD operations
    path('add/<slug:post_slug>/', views.add_comment, name='add_comment'),
    path('edit/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    
    # Comment interactions
    path('like/<int:comment_id>/', views.like_comment, name='like_comment'),
    path('flag/<int:comment_id>/', views.flag_comment, name='flag_comment'),
]
