#!/usr/bin/env python
"""Create sample data for the blog."""

import os
import sys
import django
from django.utils import timezone
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_blog.settings')
django.setup()

from django.contrib.auth.models import User
from blog.models import Category, BlogPost
from users.models import UserProfile

def create_sample_data():
    """Create sample blog data."""
    
    # Create categories
    categories_data = [
        {
            'name': 'Technology',
            'description': 'Latest trends in technology and programming',
            'color': '#3b82f6',
            'icon': 'fas fa-laptop-code',
            'is_featured': True
        },
        {
            'name': 'Lifestyle',
            'description': 'Tips and insights for better living',
            'color': '#10b981',
            'icon': 'fas fa-heart',
            'is_featured': True
        },
        {
            'name': 'Travel',
            'description': 'Explore the world through our travel stories',
            'color': '#f59e0b',
            'icon': 'fas fa-plane',
            'is_featured': True
        },
        {
            'name': 'Food',
            'description': 'Delicious recipes and food experiences',
            'color': '#ef4444',
            'icon': 'fas fa-utensils',
            'is_featured': False
        },
        {
            'name': 'Business',
            'description': 'Entrepreneurship and business insights',
            'color': '#8b5cf6',
            'icon': 'fas fa-briefcase',
            'is_featured': False
        }
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        categories.append(category)
        if created:
            print(f"Created category: {category.name}")
    
    # Create sample users
    users_data = [
        {
            'username': 'john_doe',
            'email': 'john@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'bio': 'Tech enthusiast and software developer with 5+ years of experience.'
        },
        {
            'username': 'jane_smith',
            'email': 'jane@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'bio': 'Travel blogger and photographer exploring the world one destination at a time.'
        },
        {
            'username': 'mike_wilson',
            'email': 'mike@example.com',
            'first_name': 'Mike',
            'last_name': 'Wilson',
            'bio': 'Food critic and chef sharing culinary adventures and recipes.'
        }
    ]
    
    users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'password': 'pbkdf2_sha256$600000$dummy$dummy'  # Dummy password
            }
        )
        if created:
            # Update profile
            profile = user.profile
            profile.bio = user_data['bio']
            profile.save()
            print(f"Created user: {user.username}")
        users.append(user)
    
    # Create sample blog posts
    posts_data = [
        {
            'title': 'Getting Started with Django: A Comprehensive Guide',
            'content': '''
            <h2>Introduction to Django</h2>
            <p>Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design. Built by experienced developers, it takes care of much of the hassle of web development, so you can focus on writing your app without needing to reinvent the wheel.</p>
            
            <h3>Why Choose Django?</h3>
            <ul>
                <li>Fast development</li>
                <li>Secure by default</li>
                <li>Scalable architecture</li>
                <li>Excellent documentation</li>
            </ul>
            
            <h3>Getting Started</h3>
            <p>To start with Django, you'll need Python installed on your system. Then you can install Django using pip:</p>
            <pre><code>pip install django</code></pre>
            
            <p>This guide will walk you through creating your first Django project and understanding the core concepts.</p>
            ''',
            'category': 'Technology',
            'author': 'john_doe',
            'tags': ['django', 'python', 'web-development', 'tutorial'],
            'is_featured': True,
            'status': 'published'
        },
        {
            'title': '10 Essential Travel Tips for First-Time Backpackers',
            'content': '''
            <h2>Your First Backpacking Adventure</h2>
            <p>Backpacking can be one of the most rewarding ways to travel, offering freedom, adventure, and unforgettable experiences. Here are essential tips for first-time backpackers.</p>
            
            <h3>1. Pack Light</h3>
            <p>The golden rule of backpacking is to pack only what you absolutely need. Your back will thank you later!</p>
            
            <h3>2. Research Your Destination</h3>
            <p>Understanding local customs, weather, and safety considerations is crucial for a successful trip.</p>
            
            <h3>3. Budget Wisely</h3>
            <p>Plan your budget carefully and always have a contingency fund for emergencies.</p>
            
            <p>Remember, the best adventures often come from stepping out of your comfort zone!</p>
            ''',
            'category': 'Travel',
            'author': 'jane_smith',
            'tags': ['travel', 'backpacking', 'adventure', 'tips'],
            'is_featured': True,
            'status': 'published'
        },
        {
            'title': 'The Art of Italian Pasta: From Tradition to Innovation',
            'content': '''
            <h2>A Culinary Journey Through Italy</h2>
            <p>Italian pasta is more than just food; it's a cultural heritage that has been passed down through generations. Each region of Italy has its own unique pasta traditions and recipes.</p>
            
            <h3>Traditional Pasta Making</h3>
            <p>The art of making pasta by hand is a skill that requires patience and practice. The key ingredients are simple: flour, eggs, and a pinch of salt.</p>
            
            <h3>Regional Variations</h3>
            <ul>
                <li><strong>Northern Italy:</strong> Rich, creamy sauces with butter and cheese</li>
                <li><strong>Central Italy:</strong> Simple, rustic preparations with olive oil and herbs</li>
                <li><strong>Southern Italy:</strong> Tomato-based sauces with fresh vegetables</li>
            </ul>
            
            <p>Modern chefs are now innovating while respecting tradition, creating exciting new interpretations of classic dishes.</p>
            ''',
            'category': 'Food',
            'author': 'mike_wilson',
            'tags': ['food', 'italian', 'pasta', 'cooking', 'tradition'],
            'is_featured': False,
            'status': 'published'
        },
        {
            'title': 'Building a Sustainable Business in 2024',
            'content': '''
            <h2>The Future of Business is Sustainable</h2>
            <p>As we move into 2024, sustainability is no longer just a buzzword—it's a business imperative. Companies that embrace sustainable practices are not only helping the planet but also building stronger, more resilient businesses.</p>
            
            <h3>Key Principles of Sustainable Business</h3>
            <ol>
                <li>Environmental responsibility</li>
                <li>Social impact</li>
                <li>Economic viability</li>
                <li>Stakeholder engagement</li>
            </ol>
            
            <h3>Implementation Strategies</h3>
            <p>Start small and scale up. Focus on areas where you can make the biggest impact with the resources you have available.</p>
            
            <p>Remember, sustainability is a journey, not a destination. Every step counts!</p>
            ''',
            'category': 'Business',
            'author': 'john_doe',
            'tags': ['business', 'sustainability', 'entrepreneurship', '2024'],
            'is_featured': False,
            'status': 'published'
        },
        {
            'title': 'Mindful Living: Simple Practices for a Better Life',
            'content': '''
            <h2>Embracing Mindfulness in Daily Life</h2>
            <p>In our fast-paced world, mindfulness offers a way to slow down, be present, and find peace in the moment. These simple practices can transform your daily experience.</p>
            
            <h3>Morning Mindfulness</h3>
            <p>Start your day with intention. Take five minutes to breathe deeply and set positive intentions for the day ahead.</p>
            
            <h3>Mindful Eating</h3>
            <p>Pay attention to your food. Notice the colors, textures, and flavors. Eat slowly and appreciate each bite.</p>
            
            <h3>Evening Reflection</h3>
            <p>End your day by reflecting on three things you're grateful for. This simple practice can shift your perspective and improve your overall well-being.</p>
            
            <p>Remember, mindfulness is a practice. Be patient with yourself as you develop these new habits.</p>
            ''',
            'category': 'Lifestyle',
            'author': 'jane_smith',
            'tags': ['mindfulness', 'wellness', 'lifestyle', 'meditation'],
            'is_featured': True,
            'status': 'published'
        }
    ]
    
    # Create posts
    for i, post_data in enumerate(posts_data):
        category = Category.objects.get(name=post_data['category'])
        author = User.objects.get(username=post_data['author'])
        
        post, created = BlogPost.objects.get_or_create(
            title=post_data['title'],
            defaults={
                'content': post_data['content'],
                'category': category,
                'author': author,
                'status': post_data['status'],
                'is_featured': post_data['is_featured'],
                'published_at': timezone.now() - timedelta(days=i*2),
                'view_count': (i + 1) * 50,
                'like_count': (i + 1) * 10,
            }
        )
        
        if created:
            # Add tags
            for tag_name in post_data['tags']:
                post.tags.add(tag_name)
            print(f"Created post: {post.title}")
    
    print("\nSample data created successfully!")
    print("You can now run the server with: python manage.py runserver")

if __name__ == '__main__':
    create_sample_data()
