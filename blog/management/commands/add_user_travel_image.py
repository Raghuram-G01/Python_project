"""Management command to add user's travel image to the travel post."""

import os
import base64
from io import BytesIO
from PIL import Image
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from blog.models import BlogPost


class Command(BaseCommand):
    help = 'Add user provided travel image to the travel post'

    def add_arguments(self, parser):
        parser.add_argument(
            '--image-path',
            type=str,
            help='Path to the travel image file',
        )

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

        # If image path is provided, use that
        if options['image_path'] and os.path.exists(options['image_path']):
            try:
                with open(options['image_path'], 'rb') as f:
                    image_content = f.read()
                
                # Remove old image if exists
                if travel_post.featured_image:
                    travel_post.featured_image.delete(save=False)
                
                # Save new image
                filename = f"{travel_post.slug}-user-image.jpg"
                travel_post.featured_image.save(
                    filename,
                    ContentFile(image_content),
                    save=False
                )
                
                travel_post.featured_image_alt = "Beautiful travel destinations with world landmarks, tropical scenery, and adventure elements"
                travel_post.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Updated travel post with user image: "{travel_post.title}"')
                )
                return
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to process user image: {str(e)}')
                )
        
        # If no image path provided, create a beautiful travel composite image
        # that represents the user's travel image concept
        try:
            img = self.create_travel_composite()
            
            # Save the image to BytesIO
            img_io = BytesIO()
            img.save(img_io, format='JPEG', quality=95)
            img_io.seek(0)
            
            # Create filename
            filename = f"{travel_post.slug}-travel-composite.jpg"
            
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
            travel_post.featured_image_alt = "Stunning travel composite featuring world landmarks, tropical paradise, and adventure destinations"
            travel_post.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Updated travel post with composite travel image: "{travel_post.title}"')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to create travel composite: {str(e)}')
            )

    def create_travel_composite(self):
        """Create a travel composite image inspired by the user's travel image."""
        from PIL import ImageDraw, ImageFont, ImageFilter
        
        # Image dimensions - wide format like the user's image
        width, height = 1400, 600
        
        # Create base image with beautiful sky gradient
        img = Image.new('RGB', (width, height), (135, 206, 250))  # Deep sky blue
        draw = ImageDraw.Draw(img)
        
        # Create sky gradient (deep blue to light blue)
        for y in range(height // 2):
            alpha = y / (height // 2)
            r = int(70 * (1 - alpha) + 173 * alpha)
            g = int(130 * (1 - alpha) + 216 * alpha)
            b = int(180 * (1 - alpha) + 230 * alpha)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Add water/ocean (bottom portion)
        water_start = height // 2 + 50
        for y in range(water_start, height):
            alpha = (y - water_start) / (height - water_start)
            r = int(64 * (1 - alpha) + 25 * alpha)
            g = int(164 * (1 - alpha) + 118 * alpha)
            b = int(223 * (1 - alpha) + 210 * alpha)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Add fluffy clouds
        cloud_positions = [
            (200, 80, 120, 40),
            (500, 60, 140, 50),
            (900, 90, 100, 35),
            (1200, 70, 130, 45)
        ]
        
        for x, y, w, h in cloud_positions:
            # Multiple overlapping ellipses for fluffy effect
            draw.ellipse([x-w//2, y-h//2, x+w//2, y+h//2], fill=(255, 255, 255, 220))
            draw.ellipse([x-w//3, y-h//3, x+w//3, y+h//3], fill=(255, 255, 255))
            draw.ellipse([x-w//4, y-h//4, x+w//4, y+h//4], fill=(248, 248, 255))
        
        # Add sun with rays
        sun_x, sun_y = width - 200, 120
        # Sun glow
        for radius in range(60, 30, -5):
            alpha = (60 - radius) / 30
            color_intensity = int(255 * alpha)
            draw.ellipse([
                sun_x - radius, sun_y - radius,
                sun_x + radius, sun_y + radius
            ], fill=(255, 255 - color_intensity//3, 0))
        
        # Sun rays
        import math
        for angle in range(0, 360, 30):
            x1 = sun_x + 70 * math.cos(math.radians(angle))
            y1 = sun_y + 70 * math.sin(math.radians(angle))
            x2 = sun_x + 100 * math.cos(math.radians(angle))
            y2 = sun_y + 100 * math.sin(math.radians(angle))
            draw.line([(x1, y1), (x2, y2)], fill=(255, 223, 0), width=4)
        
        # Add palm tree (left side)
        palm_x, palm_y = 120, height - 50
        # Tree trunk with texture
        trunk_color = (101, 67, 33)
        draw.rectangle([palm_x-12, palm_y-180, palm_x+12, palm_y], fill=trunk_color)
        # Add trunk segments
        for i in range(0, 180, 20):
            draw.line([(palm_x-12, palm_y-i), (palm_x+12, palm_y-i)], fill=(80, 50, 20), width=2)
        
        # Palm fronds
        frond_color = (34, 139, 34)
        frond_positions = [
            (-60, -200, -10, -160),  # Left
            (10, -200, 60, -160),    # Right
            (-30, -220, 30, -180),   # Top
            (-45, -190, -5, -150),   # Left-mid
            (5, -190, 45, -150),     # Right-mid
        ]
        
        for x1, y1, x2, y2 in frond_positions:
            # Create curved fronds
            points = []
            for t in range(11):
                t_norm = t / 10
                x = palm_x + x1 + (x2 - x1) * t_norm
                y = palm_y + y1 + (y2 - y1) * t_norm + 10 * math.sin(t_norm * math.pi)
                points.append((x, y))
            
            if len(points) > 1:
                draw.line(points, fill=frond_color, width=8)
        
        # Add world landmarks silhouettes
        landmarks_y = height // 2 + 20
        
        # Eiffel Tower
        tower_x = width // 2 - 200
        draw.polygon([
            (tower_x, landmarks_y),
            (tower_x + 8, landmarks_y - 120),
            (tower_x + 16, landmarks_y - 120),
            (tower_x + 24, landmarks_y)
        ], fill=(40, 40, 40))
        # Tower details
        draw.line([(tower_x + 4, landmarks_y - 40), (tower_x + 20, landmarks_y - 40)], fill=(40, 40, 40), width=2)
        draw.line([(tower_x + 6, landmarks_y - 80), (tower_x + 18, landmarks_y - 80)], fill=(40, 40, 40), width=2)
        
        # Big Ben / Clock Tower
        ben_x = width // 2 - 100
        draw.rectangle([ben_x, landmarks_y - 100, ben_x + 20, landmarks_y], fill=(40, 40, 40))
        draw.rectangle([ben_x + 5, landmarks_y - 110, ben_x + 15, landmarks_y - 100], fill=(40, 40, 40))
        
        # Statue of Liberty
        liberty_x = width // 2
        draw.rectangle([liberty_x, landmarks_y - 80, liberty_x + 8, landmarks_y], fill=(40, 40, 40))
        draw.polygon([
            (liberty_x - 10, landmarks_y - 90),
            (liberty_x + 4, landmarks_y - 100),
            (liberty_x + 18, landmarks_y - 90)
        ], fill=(40, 40, 40))
        
        # Modern buildings skyline
        building_heights = [60, 80, 70, 90, 75, 85, 65]
        for i, building_height in enumerate(building_heights):
            building_x = width // 2 + 50 + i * 35
            draw.rectangle([
                building_x, landmarks_y - building_height,
                building_x + 30, landmarks_y
            ], fill=(40, 40, 40))
            # Add windows
            for window_y in range(landmarks_y - building_height + 10, landmarks_y - 10, 15):
                for window_x in range(building_x + 5, building_x + 25, 8):
                    draw.rectangle([
                        window_x, window_y,
                        window_x + 4, window_y + 6
                    ], fill=(255, 255, 0))
        
        # Add pyramid
        pyramid_x = width // 2 + 300
        draw.polygon([
            (pyramid_x, landmarks_y),
            (pyramid_x + 30, landmarks_y),
            (pyramid_x + 15, landmarks_y - 60)
        ], fill=(40, 40, 40))
        
        # Add airplane with contrail
        plane_x, plane_y = width - 400, 180
        # Airplane body
        draw.ellipse([plane_x-15, plane_y-4, plane_x+15, plane_y+4], fill=(200, 200, 200))
        # Wings
        draw.ellipse([plane_x-12, plane_y-12, plane_x+12, plane_y-6], fill=(200, 200, 200))
        draw.ellipse([plane_x-12, plane_y+6, plane_x+12, plane_y+12], fill=(200, 200, 200))
        
        # Contrail
        contrail_points = []
        for i in range(80):
            x = plane_x - 25 - i * 4
            y = plane_y + math.sin(i * 0.1) * 3
            contrail_points.append((x, y))
        if len(contrail_points) > 1:
            draw.line(contrail_points, fill=(255, 255, 255), width=3)
        
        # Add heart-shaped cloud (like in the original image)
        heart_x, heart_y = width - 300, 100
        # Create heart shape with two circles and a triangle
        draw.ellipse([heart_x-20, heart_y-10, heart_x, heart_y+10], fill=(255, 255, 255))
        draw.ellipse([heart_x, heart_y-10, heart_x+20, heart_y+10], fill=(255, 255, 255))
        draw.polygon([
            (heart_x-15, heart_y+5),
            (heart_x+15, heart_y+5),
            (heart_x, heart_y+25)
        ], fill=(255, 255, 255))
        
        # Add birds in the sky
        bird_positions = [(300, 150), (320, 140), (340, 155), (800, 120), (820, 115)]
        for bx, by in bird_positions:
            # Simple V-shaped birds
            draw.line([(bx-5, by), (bx, by-3), (bx+5, by)], fill=(80, 80, 80), width=2)
        
        return img
