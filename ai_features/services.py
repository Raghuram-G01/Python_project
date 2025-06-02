"""AI Services for the blog application."""

import openai
import logging
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from transformers import pipeline, AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
import torch
import numpy as np
from textstat import flesch_reading_ease, flesch_kincaid_grade
import yake
import re
from django.core.cache import cache

logger = logging.getLogger('ai_features')


class OpenAIService:
    """Service for OpenAI API interactions"""

    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_content(self, prompt: str, max_tokens: int = 1000,
                         temperature: float = 0.7) -> Dict:
        """Generate content using GPT"""
        try:
            response = self.client.chat.completions.create(
                model=settings.AI_MODELS['content_generator'],
                messages=[
                    {"role": "system", "content": "You are a professional blog writer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )

            return {
                'success': True,
                'content': response.choices[0].message.content,
                'usage': response.usage.dict() if response.usage else {},
                'model': response.model
            }
        except Exception as e:
            logger.error(f"OpenAI content generation error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def moderate_content(self, text: str) -> Dict:
        """Moderate content using OpenAI moderation API"""
        try:
            response = self.client.moderations.create(
                input=text,
                model=settings.AI_MODELS['moderation']
            )

            result = response.results[0]
            return {
                'success': True,
                'flagged': result.flagged,
                'categories': result.categories.dict(),
                'category_scores': result.category_scores.dict()
            }
        except Exception as e:
            logger.error(f"OpenAI moderation error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def generate_summary(self, text: str, max_length: int = 150) -> Dict:
        """Generate summary using GPT"""
        prompt = f"""
        Please provide a concise summary of the following text in {max_length} words or less:

        {text}

        Summary:
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system",
                        "content": "You are a professional content summarizer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_length * 2,
                temperature=0.3
            )

            return {
                'success': True,
                'summary': response.choices[0].message.content.strip(),
                'usage': response.usage.dict() if response.usage else {}
            }
        except Exception as e:
            logger.error(f"OpenAI summarization error: {str(e)}")
            return {'success': False, 'error': str(e)}


class HuggingFaceService:
    """Service for HuggingFace model interactions"""

    def __init__(self):
        self.summarizer = None
        self.sentiment_analyzer = None
        self.embedding_model = None

    def get_summarizer(self):
        """Lazy load summarization model"""
        if self.summarizer is None:
            cache_key = 'hf_summarizer'
            self.summarizer = cache.get(cache_key)
            if self.summarizer is None:
                self.summarizer = pipeline(
                    "summarization",
                    model=settings.AI_MODELS['summarizer'],
                    device=0 if torch.cuda.is_available() else -1
                )
                cache.set(cache_key, self.summarizer, 3600)  # Cache for 1 hour
        return self.summarizer

    def get_sentiment_analyzer(self):
        """Lazy load sentiment analysis model"""
        if self.sentiment_analyzer is None:
            cache_key = 'hf_sentiment'
            self.sentiment_analyzer = cache.get(cache_key)
            if self.sentiment_analyzer is None:
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model=settings.AI_MODELS['sentiment_analyzer'],
                    device=0 if torch.cuda.is_available() else -1
                )
                cache.set(cache_key, self.sentiment_analyzer, 3600)
        return self.sentiment_analyzer

    def get_embedding_model(self):
        """Lazy load embedding model"""
        if self.embedding_model is None:
            cache_key = 'embedding_model'
            self.embedding_model = cache.get(cache_key)
            if self.embedding_model is None:
                self.embedding_model = SentenceTransformer(
                    settings.AI_MODELS['embeddings']
                )
                cache.set(cache_key, self.embedding_model, 3600)
        return self.embedding_model

    def summarize_text(self, text: str, max_length: int = 150,
                       min_length: int = 50) -> Dict:
        """Summarize text using HuggingFace model"""
        try:
            summarizer = self.get_summarizer()

            # Split long text into chunks if needed
            max_chunk_length = 1024
            if len(text) > max_chunk_length:
                chunks = [text[i:i+max_chunk_length]
                          for i in range(0, len(text), max_chunk_length)]
                summaries = []

                for chunk in chunks:
                    result = summarizer(
                        chunk,
                        max_length=max_length // len(chunks),
                        min_length=min_length // len(chunks),
                        do_sample=False
                    )
                    summaries.append(result[0]['summary_text'])

                # Combine and re-summarize if needed
                combined = ' '.join(summaries)
                if len(combined) > max_length * 2:
                    final_result = summarizer(
                        combined,
                        max_length=max_length,
                        min_length=min_length,
                        do_sample=False
                    )
                    summary = final_result[0]['summary_text']
                else:
                    summary = combined
            else:
                result = summarizer(
                    text,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False
                )
                summary = result[0]['summary_text']

            return {
                'success': True,
                'summary': summary,
                'original_length': len(text),
                'summary_length': len(summary)
            }
        except Exception as e:
            logger.error(f"HuggingFace summarization error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        try:
            analyzer = self.get_sentiment_analyzer()
            result = analyzer(text)

            return {
                'success': True,
                'sentiment': result[0]['label'],
                'confidence': result[0]['score']
            }
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def generate_embeddings(self, texts: List[str]) -> Dict:
        """Generate embeddings for texts"""
        try:
            model = self.get_embedding_model()
            embeddings = model.encode(texts)

            return {
                'success': True,
                'embeddings': embeddings.tolist(),
                'dimension': embeddings.shape[1]
            }
        except Exception as e:
            logger.error(f"Embedding generation error: {str(e)}")
            return {'success': False, 'error': str(e)}


class SEOAnalysisService:
    """Service for SEO analysis and optimization"""

    def __init__(self):
        self.openai_service = OpenAIService()

    def analyze_content(self, title: str, content: str,
                        meta_description: str = "") -> Dict:
        """Comprehensive SEO analysis of content"""
        try:
            # Basic metrics
            word_count = len(content.split())
            char_count = len(content)

            # Readability analysis
            readability = self._analyze_readability(content)

            # Keyword analysis
            keywords = self._extract_keywords(content)

            # Content structure analysis
            structure = self._analyze_structure(content)

            # Meta optimization
            meta_analysis = self._analyze_meta_tags(
                title, meta_description, content)

            # Calculate overall score
            overall_score = self._calculate_seo_score(
                readability, keywords, structure, meta_analysis
            )

            # Generate suggestions
            suggestions = self._generate_seo_suggestions(
                title, content, meta_description, keywords, readability
            )

            return {
                'success': True,
                'overall_score': overall_score,
                'word_count': word_count,
                'char_count': char_count,
                'readability': readability,
                'keywords': keywords,
                'structure': structure,
                'meta_analysis': meta_analysis,
                'suggestions': suggestions
            }
        except Exception as e:
            logger.error(f"SEO analysis error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _analyze_readability(self, content: str) -> Dict:
        """Analyze content readability"""
        try:
            flesch_ease = flesch_reading_ease(content)
            flesch_grade = flesch_kincaid_grade(content)

            # Determine readability level
            if flesch_ease >= 90:
                level = "Very Easy"
            elif flesch_ease >= 80:
                level = "Easy"
            elif flesch_ease >= 70:
                level = "Fairly Easy"
            elif flesch_ease >= 60:
                level = "Standard"
            elif flesch_ease >= 50:
                level = "Fairly Difficult"
            elif flesch_ease >= 30:
                level = "Difficult"
            else:
                level = "Very Difficult"

            return {
                'flesch_ease_score': flesch_ease,
                'flesch_grade_level': flesch_grade,
                'readability_level': level,
                'score': min(flesch_ease / 100, 1.0)  # Normalize to 0-1
            }
        except Exception as e:
            logger.error(f"Readability analysis error: {str(e)}")
            return {'score': 0.5, 'error': str(e)}

    def _extract_keywords(self, content: str, max_keywords: int = 20) -> Dict:
        """Extract keywords using YAKE"""
        try:
            kw_extractor = yake.KeywordExtractor(
                lan="en",
                n=3,  # n-gram size
                dedupLim=0.7,
                top=max_keywords
            )

            keywords = kw_extractor.extract_keywords(content)

            # Format keywords with scores
            keyword_list = [
                {'keyword': kw[1], 'score': round(1 / (1 + kw[0]), 3)}
                for kw in keywords
            ]

            return {
                'keywords': keyword_list,
                'keyword_count': len(keyword_list),
                'score': min(len(keyword_list) / max_keywords, 1.0)
            }
        except Exception as e:
            logger.error(f"Keyword extraction error: {str(e)}")
            return {'keywords': [], 'score': 0.0, 'error': str(e)}

    def _analyze_structure(self, content: str) -> Dict:
        """Analyze content structure"""
        try:
            # Count headings
            h1_count = len(re.findall(
                r'<h1[^>]*>.*?</h1>', content, re.IGNORECASE))
            h2_count = len(re.findall(
                r'<h2[^>]*>.*?</h2>', content, re.IGNORECASE))
            h3_count = len(re.findall(
                r'<h3[^>]*>.*?</h3>', content, re.IGNORECASE))

            # Count paragraphs
            paragraph_count = len(re.findall(
                r'<p[^>]*>.*?</p>', content, re.IGNORECASE))

            # Count lists
            list_count = len(re.findall(
                r'<[uo]l[^>]*>.*?</[uo]l>', content, re.IGNORECASE))

            # Calculate structure score
            structure_score = 0.0
            if h1_count == 1:  # Exactly one H1
                structure_score += 0.3
            if h2_count >= 2:  # At least 2 H2s
                structure_score += 0.3
            if paragraph_count >= 3:  # At least 3 paragraphs
                structure_score += 0.2
            if list_count >= 1:  # At least one list
                structure_score += 0.2

            return {
                'h1_count': h1_count,
                'h2_count': h2_count,
                'h3_count': h3_count,
                'paragraph_count': paragraph_count,
                'list_count': list_count,
                'score': structure_score
            }
        except Exception as e:
            logger.error(f"Structure analysis error: {str(e)}")
            return {'score': 0.0, 'error': str(e)}

    def _analyze_meta_tags(self, title: str, meta_description: str,
                           content: str) -> Dict:
        """Analyze meta tags optimization"""
        try:
            score = 0.0
            issues = []

            # Title analysis
            title_length = len(title)
            if 30 <= title_length <= 60:
                score += 0.4
            else:
                issues.append(
                    f"Title length ({title_length}) should be 30-60 characters")

            # Meta description analysis
            meta_length = len(meta_description)
            if 120 <= meta_length <= 160:
                score += 0.3
            elif meta_description:
                issues.append(
                    f"Meta description length ({meta_length}) should be 120-160 characters")
            else:
                issues.append("Meta description is missing")

            # Check if title appears in content
            if title.lower() in content.lower():
                score += 0.3
            else:
                issues.append("Title should appear in content")

            return {
                'title_length': title_length,
                'meta_description_length': meta_length,
                'score': score,
                'issues': issues
            }
        except Exception as e:
            logger.error(f"Meta analysis error: {str(e)}")
            return {'score': 0.0, 'error': str(e)}

    def _calculate_seo_score(self, readability: Dict, keywords: Dict,
                             structure: Dict, meta_analysis: Dict) -> float:
        """Calculate overall SEO score"""
        weights = {
            'readability': 0.25,
            'keywords': 0.25,
            'structure': 0.25,
            'meta': 0.25
        }

        score = (
            readability.get('score', 0) * weights['readability'] +
            keywords.get('score', 0) * weights['keywords'] +
            structure.get('score', 0) * weights['structure'] +
            meta_analysis.get('score', 0) * weights['meta']
        )

        return round(score * 100, 1)  # Convert to percentage

    def _generate_seo_suggestions(self, title: str, content: str,
                                  meta_description: str, keywords: Dict,
                                  readability: Dict) -> List[str]:
        """Generate SEO improvement suggestions"""
        suggestions = []

        # Title suggestions
        if len(title) < 30:
            suggestions.append(
                "Consider making your title longer (30-60 characters)")
        elif len(title) > 60:
            suggestions.append(
                "Consider shortening your title (30-60 characters)")

        # Meta description suggestions
        if not meta_description:
            suggestions.append("Add a meta description (120-160 characters)")
        elif len(meta_description) < 120:
            suggestions.append(
                "Expand your meta description (120-160 characters)")
        elif len(meta_description) > 160:
            suggestions.append(
                "Shorten your meta description (120-160 characters)")

        # Content length suggestions
        word_count = len(content.split())
        if word_count < 300:
            suggestions.append(
                "Consider adding more content (aim for 300+ words)")

        # Readability suggestions
        if readability.get('flesch_ease_score', 50) < 60:
            suggestions.append(
                "Consider simplifying your language for better readability")

        # Keyword suggestions
        if len(keywords.get('keywords', [])) < 5:
            suggestions.append(
                "Consider adding more relevant keywords to your content")

        return suggestions
