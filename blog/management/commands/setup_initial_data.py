"""Management command to set up initial blog data."""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from blog.models import Category, Tag, BlogPost
from ai_features.models import ContentTemplate


class Command(BaseCommand):
    help = 'Set up initial data for the AI blog'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up initial data...'))

        # Create categories
        categories_data = [
            {'name': 'Technology', 'description': 'Latest tech trends and innovations'},
            {'name': 'AI & Machine Learning',
                'description': 'Artificial intelligence and ML topics'},
            {'name': 'Web Development',
                'description': 'Web development tutorials and tips'},
            {'name': 'Data Science', 'description': 'Data analysis and science topics'},
            {'name': 'Programming', 'description': 'Programming languages and techniques'},
            {'name': 'Tutorial', 'description': 'Step-by-step tutorials'},
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'description': cat_data['description']
                }
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create tags
        tags_data = [
            'python', 'javascript', 'django', 'react', 'ai', 'machine-learning',
            'data-science', 'web-development', 'tutorial', 'beginner',
            'advanced', 'api', 'database', 'frontend', 'backend',
            'automation', 'productivity', 'tools', 'frameworks', 'libraries'
        ]

        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'slug': slugify(tag_name)}
            )
            if created:
                self.stdout.write(f'Created tag: {tag.name}')

        # Create admin user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            self.stdout.write(f'Created admin user: {admin_user.username}')
        else:
            admin_user = User.objects.get(username='admin')

        # Create content templates
        templates_data = [
            {
                'name': 'Blog Post Template',
                'template_type': 'blog_post',
                'description': 'Standard blog post template',
                'prompt_template': '''Write a comprehensive blog post about "{prompt}".

Structure the post with:
1. An engaging introduction
2. Main content with clear headings
3. Practical examples or tips
4. A compelling conclusion

Make it informative, engaging, and SEO-friendly. Target length: 800-1200 words.''',
                'tone_settings': {'tone': 'professional', 'style': 'informative'}
            },
            {
                'name': 'Tutorial Template',
                'template_type': 'tutorial',
                'description': 'Step-by-step tutorial template',
                'prompt_template': '''Create a detailed tutorial on "{prompt}".

Include:
1. Prerequisites and requirements
2. Step-by-step instructions with code examples
3. Common troubleshooting tips
4. Next steps or advanced topics

Make it beginner-friendly with clear explanations.''',
                'tone_settings': {'tone': 'instructional', 'style': 'step-by-step'}
            },
            {
                'name': 'Listicle Template',
                'template_type': 'listicle',
                'description': 'List-based article template',
                'prompt_template': '''Write an engaging listicle about "{prompt}".

Format as a numbered list with:
1. Catchy title with number
2. Brief introduction
3. Each list item with detailed explanation
4. Conclusion summarizing key points

Make it scannable and shareable.''',
                'tone_settings': {'tone': 'casual', 'style': 'engaging'}
            }
        ]

        for template_data in templates_data:
            template, created = ContentTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    'template_type': template_data['template_type'],
                    'description': template_data['description'],
                    'prompt_template': template_data['prompt_template'],
                    'tone_settings': template_data['tone_settings'],
                    'created_by': admin_user
                }
            )
            if created:
                self.stdout.write(f'Created template: {template.name}')

        # Create sample blog posts
        sample_posts = [
            {
                'title': 'Getting Started with AI-Powered Blogging',
                'content': '''# Welcome to the Future of Content Creation

Artificial Intelligence is revolutionizing how we create and consume content. This AI-powered blog platform demonstrates the incredible potential of combining human creativity with machine intelligence.

## What Makes This Different?

Our platform integrates several AI technologies:

- **Content Generation**: AI assists in creating high-quality blog posts
- **Smart Summarization**: Automatic generation of post summaries
- **SEO Optimization**: AI-powered SEO analysis and recommendations
- **Semantic Search**: Find content using natural language queries
- **Personalized Recommendations**: AI curates content based on your interests

## The Power of AI Writing

AI doesn't replace human creativity—it enhances it. Writers can use AI to:

1. Overcome writer's block
2. Generate ideas and outlines
3. Improve content quality
4. Optimize for search engines
5. Create content faster

## Getting Started

Ready to experience AI-powered blogging? Here's how to begin:

1. **Explore**: Browse our AI-generated and human-written content
2. **Create**: Use our AI writing assistant to create your first post
3. **Optimize**: Leverage our SEO analyzer to improve your content
4. **Engage**: Use our AI chatbot for instant assistance

The future of content creation is here, and it's more exciting than ever!''',
                'category': 'AI & Machine Learning',
                'tags': ['ai', 'blogging', 'content-creation', 'tutorial'],
                'ai_generated': True
            },
            {
                'title': 'Building Modern Web Applications with Django and AI',
                'content': '''# Django Meets Artificial Intelligence

Django, Python's premier web framework, provides an excellent foundation for building AI-powered applications. In this post, we'll explore how to integrate AI capabilities into your Django projects.

## Why Django for AI Applications?

Django offers several advantages for AI development:

- **Python Ecosystem**: Seamless integration with AI libraries
- **Scalability**: Handle growing AI workloads
- **Security**: Built-in security features for AI applications
- **Admin Interface**: Manage AI models and data easily

## Key AI Integrations

### 1. Machine Learning Models

```python
from transformers import pipeline

# Load a pre-trained model
classifier = pipeline("sentiment-analysis")
result = classifier("I love this AI-powered blog!")
```

### 2. Natural Language Processing

```python
import openai

def generate_content(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1000
    )
    return response.choices[0].text
```

### 3. Vector Embeddings

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(["Your text here"])
```

## Best Practices

1. **Async Processing**: Use Celery for long-running AI tasks
2. **Caching**: Cache AI results to improve performance
3. **Error Handling**: Gracefully handle AI service failures
4. **Monitoring**: Track AI usage and costs

Start building your AI-powered Django application today!''',
                'category': 'Web Development',
                'tags': ['django', 'python', 'ai', 'web-development', 'tutorial'],
                'ai_generated': False
            }
        ]

        for post_data in sample_posts:
            if not BlogPost.objects.filter(title=post_data['title']).exists():
                category = Category.objects.get(name=post_data['category'])

                post = BlogPost.objects.create(
                    title=post_data['title'],
                    slug=slugify(post_data['title']),
                    author=admin_user,
                    content=post_data['content'],
                    category=category,
                    status='published',
                    ai_generated=post_data['ai_generated']
                )

                # Add tags
                for tag_name in post_data['tags']:
                    tag, created = Tag.objects.get_or_create(
                        name=tag_name,
                        defaults={'slug': slugify(tag_name)}
                    )
                    post.tags.add(tag)

                self.stdout.write(f'Created post: {post.title}')

        self.stdout.write(
            self.style.SUCCESS('Successfully set up initial data!')
        )
