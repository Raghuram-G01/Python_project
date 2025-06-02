"""Management command to add featured images to blog posts."""

import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from blog.models import BlogPost


class Command(BaseCommand):
    help = 'Add featured images to blog posts based on their categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update images even if posts already have featured images',
        )

    def create_placeholder_image(self, category_name, post_title, color_scheme):
        """Create a placeholder image with category-specific design."""
        # Image dimensions
        width, height = 800, 600

        # Create image with gradient background
        img = Image.new('RGB', (width, height), color_scheme['bg'])
        draw = ImageDraw.Draw(img)

        # Create gradient effect
        for i in range(height):
            alpha = i / height
            r = int(color_scheme['bg'][0] * (1 - alpha) +
                    color_scheme['accent'][0] * alpha)
            g = int(color_scheme['bg'][1] * (1 - alpha) +
                    color_scheme['accent'][1] * alpha)
            b = int(color_scheme['bg'][2] * (1 - alpha) +
                    color_scheme['accent'][2] * alpha)
            draw.line([(0, i), (width, i)], fill=(r, g, b))

        # Add geometric shapes for visual interest
        if category_name == 'Technology':
            # Add circuit-like patterns
            for x in range(0, width, 100):
                for y in range(0, height, 100):
                    draw.rectangle([x+20, y+20, x+80, y+80],
                                   outline=color_scheme['accent'], width=2)
        elif category_name == 'Travel':
            # Add mountain-like shapes
            points = [(0, height), (200, 300), (400, 200),
                      (600, 350), (800, 250), (800, height)]
            draw.polygon(points, fill=color_scheme['accent'])
        elif category_name == 'Food':
            # Add circular patterns
            for x in range(100, width, 200):
                for y in range(100, height, 200):
                    draw.ellipse([x-50, y-50, x+50, y+50],
                                 outline=color_scheme['accent'], width=3)
        elif category_name == 'Lifestyle':
            # Add wave patterns
            for y in range(0, height, 50):
                points = []
                for x in range(0, width+50, 50):
                    points.append(
                        (x, y + 25 * (1 if (x//50) % 2 == 0 else -1)))
                if len(points) > 1:
                    draw.line(points, fill=color_scheme['accent'], width=2)
        elif category_name == 'Business':
            # Add grid patterns
            for x in range(0, width, 80):
                draw.line([(x, 0), (x, height)],
                          fill=color_scheme['accent'], width=1)
            for y in range(0, height, 80):
                draw.line([(0, y), (width, y)],
                          fill=color_scheme['accent'], width=1)

        # Add category label
        try:
            # Try to use a system font
            font_large = ImageFont.truetype("arial.ttf", 48)
            font_small = ImageFont.truetype("arial.ttf", 24)
        except:
            # Fallback to default font
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Add category name
        category_bbox = draw.textbbox(
            (0, 0), category_name.upper(), font=font_large)
        category_width = category_bbox[2] - category_bbox[0]
        category_x = (width - category_width) // 2
        draw.text((category_x, 100), category_name.upper(),
                  fill='white', font=font_large)

        # Add decorative line
        line_y = 180
        draw.line([(width//4, line_y), (3*width//4, line_y)],
                  fill='white', width=3)

        return img

    def get_color_scheme(self, category_name):
        """Get color scheme based on category."""
        schemes = {
            'Technology': {
                'bg': (30, 58, 138),      # Blue
                'accent': (59, 130, 246)   # Light blue
            },
            'Travel': {
                'bg': (101, 163, 13),      # Green
                'accent': (132, 204, 22)   # Light green
            },
            'Food': {
                'bg': (185, 28, 28),       # Red
                'accent': (239, 68, 68)    # Light red
            },
            'Lifestyle': {
                'bg': (126, 34, 206),      # Purple
                'accent': (168, 85, 247)   # Light purple
            },
            'Business': {
                'bg': (55, 65, 81),        # Gray
                'accent': (107, 114, 128)  # Light gray
            },
        }
        # Default to business colors
        return schemes.get(category_name, schemes['Business'])

    def handle(self, *args, **options):
        force_update = options['force']

        posts = BlogPost.objects.all()

        if not force_update:
            posts = posts.filter(featured_image__isnull=True)

        self.stdout.write(f'Processing {posts.count()} posts...')

        for i, post in enumerate(posts):
            try:
                # Determine category
                category_name = post.category.name if post.category else 'Business'

                # Get color scheme for this category
                color_scheme = self.get_color_scheme(category_name)

                # Create placeholder image
                self.stdout.write(f'Creating image for "{post.title}"...')
                img = self.create_placeholder_image(
                    category_name, post.title, color_scheme)

                # Save the image to BytesIO
                img_io = BytesIO()
                img.save(img_io, format='JPEG', quality=90)
                img_io.seek(0)

                # Create filename
                filename = f"{post.slug}-featured.jpg"

                # Save to the post
                post.featured_image.save(
                    filename,
                    ContentFile(img_io.read()),
                    save=False
                )

                # Set alt text
                post.featured_image_alt = f"{category_name} related image for {post.title}"
                post.save()

                self.stdout.write(
                    self.style.SUCCESS(f'✓ Added image to "{post.title}"')
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Failed to add image to "{post.title}": {str(e)}')
                )
                continue

        self.stdout.write(
            self.style.SUCCESS('\nFinished adding images to posts!')
        )
