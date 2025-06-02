#!/usr/bin/env python
"""
Quick test script to verify edit profile functionality
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_blog.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

def test_edit_profile():
    """Test the edit profile functionality"""
    print("🧪 Testing Edit Profile Functionality")
    print("=" * 50)
    
    # Create a test client
    client = Client()
    
    try:
        # Get admin user
        admin_user = User.objects.get(username='admin')
        print(f"✓ Found admin user: {admin_user.username}")
        
        # Test without login (should redirect to login)
        edit_url = reverse('users:profile_edit')
        print(f"📍 Edit profile URL: {edit_url}")
        
        response = client.get(edit_url)
        print(f"🔒 Without login - Status: {response.status_code}")
        
        if response.status_code == 302:
            print(f"✓ Correctly redirects to login: {response.url}")
        
        # Login as admin
        client.force_login(admin_user)
        print(f"🔑 Logged in as: {admin_user.username}")
        
        # Test with login
        response = client.get(edit_url)
        print(f"🔓 With login - Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Edit profile page loads successfully!")
            print("🎯 You can now access the edit profile page")
        else:
            print(f"❌ Error: Status code {response.status_code}")
            
        # Test profile view
        profile_url = reverse('users:profile', kwargs={'username': 'admin'})
        response = client.get(profile_url)
        print(f"👤 Profile page - Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Profile page loads successfully!")
        
        # Test change password page
        password_url = reverse('users:change_password')
        response = client.get(password_url)
        print(f"🔐 Change password page - Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Change password page loads successfully!")
            
    except User.DoesNotExist:
        print("❌ Admin user not found!")
        print("💡 Please run: python manage.py createsuperuser")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 EDIT PROFILE FUNCTIONALITY TEST COMPLETE")
    print("=" * 50)
    print("📋 Next Steps:")
    print("1. Go to: http://127.0.0.1:8000/users/login/")
    print("2. Click 'Login as Admin' button")
    print("3. Go to: http://127.0.0.1:8000/users/profile/admin/")
    print("4. Click 'Edit Profile' button")
    print("5. Test the enhanced profile editing features!")
    print("\n🔗 Direct URLs:")
    print("• Login: http://127.0.0.1:8000/users/login/")
    print("• Admin Profile: http://127.0.0.1:8000/users/profile/admin/")
    print("• Edit Profile: http://127.0.0.1:8000/users/profile/edit/")
    print("• Change Password: http://127.0.0.1:8000/users/profile/change-password/")
    
    return True

if __name__ == "__main__":
    test_edit_profile()
