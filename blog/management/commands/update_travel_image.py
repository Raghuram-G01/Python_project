"""Management command to update the travel post with a custom image."""

import os
import requests
from io import BytesIO
from PIL import Image
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from blog.models import BlogPost


class Command(BaseCommand):
    help = 'Update the travel post with a custom travel image'

    def handle(self, *args, **options):
        # Find the travel post
        try:
            travel_post = BlogPost.objects.get(
                title__icontains='travel',
                category__name='Travel'
            )
        except BlogPost.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Travel post not found!')
            )
            return
        except BlogPost.MultipleObjectsReturned:
            # Get the first travel post
            travel_post = BlogPost.objects.filter(
                title__icontains='travel',
                category__name='Travel'
            ).first()

        self.stdout.write(f'Found travel post: "{travel_post.title}"')

        # Create a beautiful travel image programmatically
        # Since we can't directly use the uploaded image, we'll create a similar one
        try:
            # Create a travel-themed image
            img = self.create_travel_image()
            
            # Save the image to BytesIO
            img_io = BytesIO()
            img.save(img_io, format='JPEG', quality=95)
            img_io.seek(0)
            
            # Create filename
            filename = f"{travel_post.slug}-custom-featured.jpg"
            
            # Remove old image if exists
            if travel_post.featured_image:
                travel_post.featured_image.delete(save=False)
            
            # Save new image to the post
            travel_post.featured_image.save(
                filename,
                ContentFile(img_io.read()),
                save=False
            )
            
            # Set alt text
            travel_post.featured_image_alt = "Beautiful travel destinations around the world with landmarks and tropical scenery"
            travel_post.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Updated travel post image: "{travel_post.title}"')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to update travel post image: {str(e)}')
            )

    def create_travel_image(self):
        """Create a beautiful travel-themed image."""
        from PIL import ImageDraw, ImageFont
        
        # Image dimensions
        width, height = 1200, 800
        
        # Create base image with sky blue gradient
        img = Image.new('RGB', (width, height), (135, 206, 235))  # Sky blue
        draw = ImageDraw.Draw(img)
        
        # Create sky gradient (blue to lighter blue)
        for y in range(height // 2):
            alpha = y / (height // 2)
            r = int(135 * (1 - alpha) + 173 * alpha)
            g = int(206 * (1 - alpha) + 216 * alpha)
            b = int(235 * (1 - alpha) + 230 * alpha)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Add water (bottom half)
        water_start = height // 2
        for y in range(water_start, height):
            alpha = (y - water_start) / (height - water_start)
            r = int(64 * (1 - alpha) + 25 * alpha)
            g = int(164 * (1 - alpha) + 118 * alpha)
            b = int(223 * (1 - alpha) + 210 * alpha)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Add clouds
        cloud_color = (255, 255, 255, 180)
        # Cloud 1
        draw.ellipse([100, 80, 200, 120], fill=(255, 255, 255))
        draw.ellipse([150, 60, 250, 100], fill=(255, 255, 255))
        draw.ellipse([180, 70, 280, 110], fill=(255, 255, 255))
        
        # Cloud 2
        draw.ellipse([800, 100, 900, 140], fill=(255, 255, 255))
        draw.ellipse([850, 80, 950, 120], fill=(255, 255, 255))
        
        # Add sun
        sun_x, sun_y = width - 150, 100
        draw.ellipse([sun_x-40, sun_y-40, sun_x+40, sun_y+40], fill=(255, 223, 0))
        
        # Add sun rays
        for angle in range(0, 360, 45):
            import math
            x1 = sun_x + 50 * math.cos(math.radians(angle))
            y1 = sun_y + 50 * math.sin(math.radians(angle))
            x2 = sun_x + 70 * math.cos(math.radians(angle))
            y2 = sun_y + 70 * math.sin(math.radians(angle))
            draw.line([(x1, y1), (x2, y2)], fill=(255, 223, 0), width=3)
        
        # Add palm tree
        palm_x, palm_y = 150, height - 100
        # Tree trunk
        draw.rectangle([palm_x-10, palm_y-200, palm_x+10, palm_y], fill=(139, 69, 19))
        
        # Palm leaves
        leaf_color = (34, 139, 34)
        # Left leaves
        draw.ellipse([palm_x-80, palm_y-250, palm_x-20, palm_y-200], fill=leaf_color)
        draw.ellipse([palm_x-70, palm_y-240, palm_x-10, palm_y-190], fill=leaf_color)
        # Right leaves
        draw.ellipse([palm_x+20, palm_y-250, palm_x+80, palm_y-200], fill=leaf_color)
        draw.ellipse([palm_x+10, palm_y-240, palm_x+70, palm_y-190], fill=leaf_color)
        # Top leaves
        draw.ellipse([palm_x-30, palm_y-280, palm_x+30, palm_y-220], fill=leaf_color)
        
        # Add airplane
        plane_x, plane_y = width - 300, 150
        # Airplane body
        draw.ellipse([plane_x-20, plane_y-5, plane_x+20, plane_y+5], fill=(192, 192, 192))
        # Wings
        draw.ellipse([plane_x-15, plane_y-15, plane_x+15, plane_y-8], fill=(192, 192, 192))
        draw.ellipse([plane_x-15, plane_y+8, plane_x+15, plane_y+15], fill=(192, 192, 192))
        
        # Add airplane trail
        trail_points = []
        for i in range(50):
            x = plane_x - 30 - i * 3
            y = plane_y + (i % 3 - 1) * 2
            trail_points.append((x, y))
        if len(trail_points) > 1:
            draw.line(trail_points, fill=(255, 255, 255), width=2)
        
        # Add islands/landmarks silhouettes
        # Eiffel Tower silhouette
        tower_x = width // 2 - 100
        tower_base = height // 2 + 50
        draw.polygon([
            (tower_x, tower_base),
            (tower_x + 5, tower_base - 100),
            (tower_x + 10, tower_base - 100),
            (tower_x + 15, tower_base)
        ], fill=(64, 64, 64))
        
        # Building silhouettes
        for i, building_height in enumerate([60, 80, 70, 90, 75]):
            building_x = width // 2 + i * 40
            building_y = height // 2 + 50
            draw.rectangle([
                building_x, building_y - building_height,
                building_x + 35, building_y
            ], fill=(64, 64, 64))
        
        # Add text overlay
        try:
            font_large = ImageFont.truetype("arial.ttf", 48)
            font_medium = ImageFont.truetype("arial.ttf", 32)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        
        # Add title text with shadow
        title = "EXPLORE THE WORLD"
        title_bbox = draw.textbbox((0, 0), title, font=font_large)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        title_y = height - 150
        
        # Text shadow
        draw.text((title_x + 2, title_y + 2), title, fill=(0, 0, 0, 128), font=font_large)
        # Main text
        draw.text((title_x, title_y), title, fill=(255, 255, 255), font=font_large)
        
        # Add subtitle
        subtitle = "Discover Amazing Destinations"
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_medium)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (width - subtitle_width) // 2
        subtitle_y = title_y + 60
        
        # Subtitle shadow
        draw.text((subtitle_x + 1, subtitle_y + 1), subtitle, fill=(0, 0, 0, 128), font=font_medium)
        # Main subtitle
        draw.text((subtitle_x, subtitle_y), subtitle, fill=(255, 255, 255), font=font_medium)
        
        return img
