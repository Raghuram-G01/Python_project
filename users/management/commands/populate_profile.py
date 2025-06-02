"""Management command to populate user profiles with sample content."""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile


class Command(BaseCommand):
    help = 'Populate user profiles with sample content'

    def handle(self, *args, **options):
        # Sample profile data for different users
        profile_data = {
            'admin': {
                'bio': """👋 Hello! I'm the administrator of this amazing blog platform. 

🚀 **About Me:**
I'm passionate about technology, web development, and creating platforms that bring people together to share knowledge and ideas. With over 5 years of experience in software development, I love building tools that make a difference.

💻 **What I Do:**
- Full-stack web development
- Blog platform management
- Community building
- Tech content creation

🌟 **Interests:**
- Python & Django development
- Modern web technologies
- Open source projects
- Digital storytelling
- Photography and travel

📚 **Currently Learning:**
- AI and Machine Learning
- Cloud architecture
- Mobile app development

Feel free to reach out if you have any questions about the platform or want to collaborate on interesting projects!""",
                'location': 'San Francisco, CA',
                'website': 'https://example-portfolio.com',
                'twitter_username': 'admin_blogger',
                'github_username': 'admin-dev',
                'linkedin_username': 'admin-professional',
                'show_email': True
            },
            'john_doe': {
                'bio': """🔧 Software Engineer & Tech Enthusiast

I'm a passionate software developer with expertise in modern web technologies. I love sharing my knowledge through detailed tutorials and insights about the latest trends in technology.

**Specialties:**
- JavaScript & React
- Node.js & Express
- Database design
- API development

When I'm not coding, you can find me exploring new technologies, contributing to open source projects, or writing about my development journey.""",
                'location': 'Austin, TX',
                'website': 'https://johndoe-dev.com',
                'twitter_username': 'john_codes',
                'github_username': 'john-doe-dev',
                'linkedin_username': 'john-doe-engineer'
            },
            'jane_smith': {
                'bio': """✈️ Travel Blogger & Digital Nomad

Exploring the world one destination at a time! I share travel tips, cultural insights, and photography from my adventures around the globe.

**Travel Stats:**
- 🌍 45+ countries visited
- 📸 10k+ photos taken
- ✍️ 200+ travel articles written
- 🎒 5+ years of nomadic life

Join me on this incredible journey as I discover hidden gems, meet amazing people, and share stories that inspire wanderlust!""",
                'location': 'Currently in: Bali, Indonesia',
                'website': 'https://wanderlust-jane.com',
                'twitter_username': 'jane_travels',
                'github_username': 'jane-photographer',
                'linkedin_username': 'jane-smith-travel'
            },
            'mike_wilson': {
                'bio': """👨‍🍳 Food Critic & Culinary Explorer

Passionate about discovering exceptional flavors and sharing culinary experiences. From street food to fine dining, I explore it all!

**Culinary Journey:**
- 🍽️ 500+ restaurants reviewed
- 🌶️ Spice tolerance: Expert level
- 📖 Published food critic
- 👨‍🍳 Amateur chef

I believe food is a universal language that brings people together. Let's explore the world of flavors together!""",
                'location': 'New York, NY',
                'website': 'https://mike-foodie.com',
                'twitter_username': 'mike_eats',
                'github_username': 'mike-recipes',
                'linkedin_username': 'mike-wilson-food'
            }
        }

        updated_count = 0
        
        for username, data in profile_data.items():
            try:
                user = User.objects.get(username=username)
                profile, created = UserProfile.objects.get_or_create(user=user)
                
                # Update profile fields
                profile.bio = data['bio']
                profile.location = data['location']
                profile.website = data['website']
                profile.twitter_username = data['twitter_username']
                profile.github_username = data['github_username']
                profile.linkedin_username = data['linkedin_username']
                profile.show_email = data.get('show_email', False)
                
                profile.save()
                updated_count += 1
                
                status = "Created" if created else "Updated"
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {status} profile for {username}')
                )
                
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠ User {username} not found, skipping...')
                )
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(f'PROFILE POPULATION COMPLETE')
        self.stdout.write('='*60)
        self.stdout.write(f'✓ Updated {updated_count} profiles')
        self.stdout.write('\nTo view the populated profiles:')
        
        for username in profile_data.keys():
            self.stdout.write(f'• http://127.0.0.1:8000/users/profile/{username}/')
        
        self.stdout.write('\nTo edit your profile:')
        self.stdout.write('• http://127.0.0.1:8000/users/profile/edit/')
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 All profiles are now populated with rich content!')
        )
