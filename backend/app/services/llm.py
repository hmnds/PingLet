"""LLM service for generating summaries and answers."""
from typing import Optional, List, Dict, Any
from openai import OpenAI
from app.config import settings
import structlog

logger = structlog.get_logger()


class LLMService:
    """Service for LLM operations using OpenAI."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        self.model = settings.llm_model
        self.client = None
        
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def generate_summary(self, text: str, max_sentences: int = 2) -> str:
        """
        Generate a 1-2 sentence summary of text.
        
        Args:
            text: Text to summarize
            max_sentences: Maximum number of sentences in summary
            
        Returns:
            Summary string
        """
        if not self.client:
            logger.warning("OpenAI API key not configured, returning truncated text")
            if len(text) > 200:
                return text[:200] + "..."
            return text
        
        try:
            prompt = f"""Summarize the following text in {max_sentences} sentences. Be concise and factual:

{text}

Summary:"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise summaries."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=150,
                temperature=0.3,
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
        except Exception as e:
            logger.error("Failed to generate summary", error=str(e))
            # Fallback to truncated text
            if len(text) > 200:
                return text[:200] + "..."
            return text

    def generate_digest(
        self,
        posts_by_author: Dict[str, List[Dict[str, Any]]],
    ) -> str:
        """
        Generate a daily digest from posts grouped by author.
        
        Args:
            posts_by_author: Dict mapping author username to list of post dicts
            
        Returns:
            Markdown formatted digest
        """
        if not self.client:
            logger.warning("OpenAI API key not configured, generating basic digest")
            return self._basic_digest(posts_by_author)
        
        try:
            # Build context
            context_parts = []
            for author, posts in posts_by_author.items():
                context_parts.append(f"\n## {author}\n")
                for post in posts:
                    context_parts.append(f"- {post['text'][:200]}")
            
            context = "\n".join(context_parts)
            
            prompt = f"""Create a daily digest from the following posts grouped by author. 
Summarize the key themes and insights. Group related posts together. 
Be concise but informative. Format as markdown with sections.

Posts:
{context}

Digest:"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates informative digests from social media posts."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2000,
                temperature=0.5,
            )
            
            digest = response.choices[0].message.content.strip()
            return digest
        except Exception as e:
            logger.error("Failed to generate digest", error=str(e))
            return self._basic_digest(posts_by_author)

    def _basic_digest(self, posts_by_author: Dict[str, List[Dict[str, Any]]]) -> str:
        """Generate a basic digest without LLM."""
        parts = ["# Daily Digest\n"]
        
        for author, posts in posts_by_author.items():
            parts.append(f"\n## {author}\n")
            for post in posts:
                text = post['text']
                if len(text) > 200:
                    text = text[:200] + "..."
                parts.append(f"- {text}\n")
        
        return "\n".join(parts)



