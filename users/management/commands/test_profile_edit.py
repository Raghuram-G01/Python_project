"""Management command to test the profile edit functionality."""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile


class Command(BaseCommand):
    help = 'Test the profile edit functionality'

    def handle(self, *args, **options):
        # Check if admin user exists
        try:
            admin_user = User.objects.get(username='admin')
            self.stdout.write(f'Found admin user: {admin_user.username}')
            
            # Check if profile exists
            try:
                profile = admin_user.profile
                self.stdout.write(f'Profile exists for admin user')
                self.stdout.write(f'Bio: {profile.bio or "Not set"}')
                self.stdout.write(f'Location: {profile.location or "Not set"}')
                self.stdout.write(f'Website: {profile.website or "Not set"}')
                
                # Update some profile information for testing
                if not profile.bio:
                    profile.bio = "Administrator of this amazing blog platform. Passionate about technology and sharing knowledge."
                    profile.location = "San Francisco, CA"
                    profile.website = "https://example.com"
                    profile.save()
                    self.stdout.write(
                        self.style.SUCCESS('✓ Updated admin profile with sample data')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS('✓ Admin profile already has data')
                    )
                    
            except UserProfile.DoesNotExist:
                # Create profile if it doesn't exist
                profile = UserProfile.objects.create(
                    user=admin_user,
                    bio="Administrator of this amazing blog platform. Passionate about technology and sharing knowledge.",
                    location="San Francisco, CA",
                    website="https://example.com"
                )
                self.stdout.write(
                    self.style.SUCCESS('✓ Created profile for admin user')
                )
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('✗ Admin user not found. Please create an admin user first.')
            )
            return
        
        # Test URLs
        self.stdout.write('\n' + '='*50)
        self.stdout.write('PROFILE EDIT FUNCTIONALITY TEST')
        self.stdout.write('='*50)
        self.stdout.write(f'Profile URL: /users/profile/{admin_user.username}/')
        self.stdout.write(f'Edit Profile URL: /users/profile/edit/')
        self.stdout.write(f'Change Password URL: /users/profile/change-password/')
        self.stdout.write('\nTo test the edit profile functionality:')
        self.stdout.write('1. Go to http://127.0.0.1:8000/admin/')
        self.stdout.write('2. Login with admin credentials')
        self.stdout.write('3. Visit http://127.0.0.1:8000/users/profile/admin/')
        self.stdout.write('4. Click "Edit Profile" button')
        self.stdout.write('5. Test the tabbed interface and form validation')
        self.stdout.write('6. Test the password change functionality')
        
        self.stdout.write(
            self.style.SUCCESS('\n✓ Profile edit functionality is ready for testing!')
        )
