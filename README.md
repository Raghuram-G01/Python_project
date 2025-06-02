# 🤖 AI-Powered Blog Platform

A modern, intelligent blogging platform that leverages artificial intelligence to enhance content creation, optimization, and user experience.

## ✨ Features

### 🧠 AI-Powered Content Creation
- **AI Blog Post Generator**: Generate high-quality content using OpenAI GPT models
- **Content Templates**: Pre-built templates for different content types
- **Smart Summarization**: Automatic generation of post summaries
- **Tone and Style Control**: Customize AI output for different audiences

### 🔍 Intelligent Search & Discovery
- **Semantic Search**: Natural language search using vector embeddings
- **Personalized Recommendations**: AI-curated content based on reading history
- **Related Posts**: AI-powered content similarity matching
- **Smart Categorization**: Automatic tagging and categorization

### 📈 SEO & Analytics
- **AI SEO Analyzer**: Comprehensive SEO analysis and recommendations
- **Readability Analysis**: Content readability scoring and suggestions
- **Keyword Extraction**: Automatic keyword identification
- **Performance Insights**: AI-powered content performance analytics

### 🛡️ Content Moderation
- **AI Comment Moderation**: Automatic detection of spam and toxic content
- **Content Safety**: Real-time content moderation using OpenAI
- **Sentiment Analysis**: Understand content and comment sentiment

### 💬 Interactive Features
- **AI Chatbot**: Intelligent assistant for user queries
- **Voice Integration**: Speech-to-text for content creation
- **Real-time Collaboration**: Multi-user editing with AI assistance

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB
- Redis (for caching and Celery)
- OpenAI API Key
- HuggingFace API Key (optional)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ai-blog
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

4. **Configure MongoDB**
```bash
# Make sure MongoDB is running
# Default connection: mongodb://localhost:27017
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Set up initial data**
```bash
python manage.py setup_initial_data
```

7. **Create a superuser**
```bash
python manage.py createsuperuser
```

8. **Start the development server**
```bash
python manage.py runserver
```

9. **Start Celery worker (in another terminal)**
```bash
celery -A ai_blog worker -l info
```

### Environment Variables

Create a `.env` file with the following variables:

```env
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_USERNAME=
MONGODB_PASSWORD=

# AI API Keys
OPENAI_API_KEY=your-openai-api-key-here
HUGGINGFACE_API_KEY=your-huggingface-api-key-here
PINECONE_API_KEY=your-pinecone-api-key-here
PINECONE_ENVIRONMENT=us-west1-gcp

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
```

## 🏗️ Architecture

### Tech Stack
- **Backend**: Django 4.2+ with MongoDB (Djongo)
- **AI/ML**: OpenAI GPT, HuggingFace Transformers, Sentence Transformers
- **Search**: Vector embeddings with Pinecone/FAISS
- **Frontend**: Tailwind CSS with vanilla JavaScript
- **Caching**: Redis
- **Task Queue**: Celery
- **Database**: MongoDB

### Project Structure
```
ai_blog/
├── ai_blog/                 # Main project settings
├── blog/                    # Core blog functionality
│   ├── models.py           # Blog models (Post, Comment, etc.)
│   ├── views.py            # Blog views and API endpoints
│   └── management/         # Management commands
├── ai_features/            # AI-powered features
│   ├── models.py          # AI task tracking models
│   ├── services.py        # AI service integrations
│   └── views.py           # AI API endpoints
├── analytics/             # Analytics and insights
├── templates/             # HTML templates
├── static/               # Static files (CSS, JS, images)
└── requirements.txt      # Python dependencies
```

## 🔧 Configuration

### AI Models Configuration

The platform supports multiple AI models that can be configured in `settings.py`:

```python
AI_MODELS = {
    'content_generator': 'gpt-3.5-turbo',
    'summarizer': 'facebook/bart-large-cnn',
    'sentiment_analyzer': 'cardiffnlp/twitter-roberta-base-sentiment-latest',
    'embeddings': 'sentence-transformers/all-MiniLM-L6-v2',
    'moderation': 'text-moderation-latest',
}
```

### Search Backend

Choose your search backend:

```python
SEARCH_BACKEND = 'semantic'  # Options: 'basic', 'semantic', 'hybrid'
VECTOR_DIMENSION = 384       # For sentence-transformers/all-MiniLM-L6-v2
```

## 📚 API Documentation

### Content Generation API
```bash
POST /api/generate-content/
{
    "prompt": "Write about AI in education",
    "template_id": 1,
    "max_tokens": 1000
}
```

### SEO Analysis API
```bash
POST /api/seo-analyze/
{
    "title": "Your post title",
    "content": "Your post content",
    "meta_description": "Your meta description"
}
```

### Semantic Search API
```bash
GET /api/search/?q=AI%20machine%20learning
```

## 🧪 Testing

Run the test suite:

```bash
python manage.py test
```

Run specific app tests:

```bash
python manage.py test blog
python manage.py test ai_features
```

## 🚀 Deployment

### Production Settings

1. Set `DEBUG=False` in production
2. Configure proper `ALLOWED_HOSTS`
3. Use environment variables for sensitive data
4. Set up proper MongoDB authentication
5. Configure Redis for production
6. Use a proper web server (nginx + gunicorn)

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models
- HuggingFace for transformer models
- Django community for the excellent framework
- All contributors and testers

## 📞 Support

For support, email support@example.com or join our Discord community.

---

**Built with ❤️ and 🤖 AI**
