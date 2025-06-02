"""Management command to create sample avatars for users."""

import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from users.models import UserProfile


class Command(BaseCommand):
    help = 'Create sample avatars for users'

    def handle(self, *args, **options):
        # Avatar configurations for different users
        avatar_configs = {
            'admin': {
                'initials': 'AD',
                'bg_color': '#3B82F6',  # Blue
                'text_color': '#FFFFFF',
                'name': 'Admin'
            },
            'john_doe': {
                'initials': 'JD',
                'bg_color': '#10B981',  # Green
                'text_color': '#FFFFFF',
                'name': 'John Doe'
            },
            'jane_smith': {
                'initials': 'JS',
                'bg_color': '#F59E0B',  # Orange
                'text_color': '#FFFFFF',
                'name': 'Jane Smith'
            },
            'mike_wilson': {
                'initials': 'MW',
                'bg_color': '#EF4444',  # Red
                'text_color': '#FFFFFF',
                'name': 'Mike Wilson'
            }
        }

        created_count = 0
        
        for username, config in avatar_configs.items():
            try:
                user = User.objects.get(username=username)
                profile = user.profile
                
                # Skip if user already has an avatar
                if profile.avatar:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ {username} already has an avatar, skipping...')
                    )
                    continue
                
                # Create avatar image
                avatar_image = self.create_avatar(
                    config['initials'],
                    config['bg_color'],
                    config['text_color']
                )
                
                # Save avatar to profile
                img_io = BytesIO()
                avatar_image.save(img_io, format='PNG', quality=95)
                img_io.seek(0)
                
                filename = f"{username}_avatar.png"
                profile.avatar.save(
                    filename,
                    ContentFile(img_io.read()),
                    save=True
                )
                
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created avatar for {config["name"]} ({username})')
                )
                
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠ User {username} not found, skipping...')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error creating avatar for {username}: {str(e)}')
                )
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(f'AVATAR CREATION COMPLETE')
        self.stdout.write('='*60)
        self.stdout.write(f'✓ Created {created_count} avatars')
        
        if created_count > 0:
            self.stdout.write('\nView the profiles with new avatars:')
            for username in avatar_configs.keys():
                self.stdout.write(f'• http://127.0.0.1:8000/users/profile/{username}/')
        
        self.stdout.write(
            self.style.SUCCESS('\n🎨 Sample avatars created successfully!')
        )

    def create_avatar(self, initials, bg_color, text_color):
        """Create a circular avatar with initials."""
        size = 400
        
        # Create image with transparent background
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Convert hex colors to RGB
        bg_rgb = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
        text_rgb = tuple(int(text_color[i:i+2], 16) for i in (1, 3, 5))
        
        # Draw circle background
        draw.ellipse([0, 0, size, size], fill=bg_rgb)
        
        # Add gradient effect
        for i in range(size//4):
            alpha = int(255 * (1 - i / (size//4)) * 0.3)
            gradient_color = (*bg_rgb, alpha)
            draw.ellipse([i, i, size-i, size-i], outline=gradient_color)
        
        # Add text (initials)
        try:
            # Try to use a nice font
            font_size = size // 3
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Get text bounding box
        bbox = draw.textbbox((0, 0), initials, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center the text
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - bbox[1]
        
        # Draw text with shadow for better visibility
        shadow_offset = 2
        draw.text((x + shadow_offset, y + shadow_offset), initials, 
                 fill=(0, 0, 0, 100), font=font)
        draw.text((x, y), initials, fill=text_rgb, font=font)
        
        # Add subtle border
        border_width = 8
        border_color = (*bg_rgb, 180)
        draw.ellipse([border_width//2, border_width//2, 
                     size-border_width//2, size-border_width//2], 
                    outline=border_color, width=border_width)
        
        return img
