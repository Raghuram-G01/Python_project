"""URL configuration for users app."""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Password reset URLs
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),

    # Profile URLs (specific paths must come before generic ones)
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/<str:username>/', views.profile_view, name='profile'),

    # Newsletter and Contact
    path('newsletter/subscribe/', views.newsletter_subscribe,
         name='newsletter_subscribe'),
    path('newsletter/subscribe/ajax/', views.newsletter_subscribe_ajax,
         name='newsletter_subscribe_ajax'),
    path('contact/', views.contact, name='contact'),

    # Authors
    path('authors/', views.authors_list, name='authors'),
]
