"""Embeddings service for generating vector embeddings."""
from typing import List, Optional
import numpy as np
from openai import OpenAI
from app.config import settings
import structlog

logger = structlog.get_logger()


class EmbeddingsService:
    """Service for generating embeddings using OpenAI."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        self.model = settings.embedding_model
        self.client = None
        
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def embed_text(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats (embedding vector) or None if API key not configured
        """
        if not self.client:
            logger.warning("OpenAI API key not configured, returning zero vector")
            return self._zero_vector()
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error("Failed to generate embedding", error=str(e))
            return self._zero_vector()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not self.client:
            logger.warning("OpenAI API key not configured, returning zero vectors")
            return [self._zero_vector() for _ in texts]
        
        if not texts:
            return []
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts,
            )
            # Sort by index to maintain order
            embeddings = sorted(response.data, key=lambda x: x.index)
            return [item.embedding for item in embeddings]
        except Exception as e:
            logger.error("Failed to generate batch embeddings", error=str(e), count=len(texts))
            return [self._zero_vector() for _ in texts]

    def _zero_vector(self) -> List[float]:
        """Return a zero vector of the expected dimension."""
        # OpenAI text-embedding-3-small has 1536 dimensions
        return [0.0] * 1536


