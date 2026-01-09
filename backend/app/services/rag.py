"""RAG service for search and chat."""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
import structlog
from app.models import Post
from app.services.embeddings import EmbeddingsService
from app.services.llm import LLMService

logger = structlog.get_logger()


class RAGService:
    """Service for RAG (Retrieval-Augmented Generation) operations."""

    def __init__(self, db: Session, embeddings_service: EmbeddingsService, llm_service: LLMService):
        self.db = db
        self.embeddings_service = embeddings_service
        self.llm_service = llm_service

    def search(self, query: str, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search posts using vector similarity for a specific user.
        
        Args:
            query: Search query text
            user_id: User ID to filter posts by
            limit: Maximum number of results
            
        Returns:
            List of post dicts with similarity scores
        """
        # Generate query embedding
        query_embedding = self.embeddings_service.embed_text(query)
        if not query_embedding:
            logger.warning("Failed to generate query embedding")
            return []
        
        # Vector search using pgvector cosine distance
        # Using <=> operator for cosine distance (1 - cosine similarity)
        # Format vector as string for pgvector: '[0.1,0.2,...]'
        vector_str = "[" + ",".join(str(v) for v in query_embedding) + "]"
        
        sql = text("""
            SELECT 
                p.id, p.x_post_id, p.author_id, p.created_at, p.text, p.url,
                1 - (p.embedding <=> :query_embedding::vector) as similarity
            FROM posts p
            JOIN monitored_accounts m ON p.author_id = m.id
            WHERE p.embedding IS NOT NULL AND m.user_id = :user_id
            ORDER BY p.embedding <=> :query_embedding::vector
            LIMIT :limit
        """)
        
        result = self.db.execute(
            sql,
            {
                "query_embedding": vector_str,
                "user_id": user_id,
                "limit": limit,
            }
        )
        
        posts = []
        for row in result:
            posts.append({
                "id": row.id,
                "x_post_id": row.x_post_id,
                "author_id": row.author_id,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "text": row.text,
                "url": row.url,
                "similarity": float(row.similarity) if row.similarity else 0.0,
            })
        
        return posts

    def chat(self, question: str, user_id: int, limit: int = 10) -> Dict[str, Any]:
        """
        Answer a question using RAG with citations.
        
        Args:
            question: User question
            user_id: User ID to filter posts by
            limit: Maximum number of posts to retrieve
            
        Returns:
            Dict with answer, citations, and retrieved posts
        """
        # Search for relevant posts within user's scope
        posts = self.search(question, user_id, limit=limit)
        
        if not posts:
            return {
                "answer": "I couldn't find any relevant posts to answer your question.",
                "citations": [],
                "posts": [],
            }
        
        # Build context from retrieved posts
        context_parts = []
        citations = []
        
        for i, post in enumerate(posts, 1):
            context_parts.append(f"[{i}] {post['text']}")
            if post['url']:
                citations.append({
                    "index": i,
                    "url": post['url'],
                    "text_preview": post['text'][:100] + "..." if len(post['text']) > 100 else post['text'],
                })
        
        context = "\n\n".join(context_parts)
        
        # Generate answer with citations
        prompt = f"""Answer the following question using ONLY the information from the posts below. 
If the answer cannot be found in the posts, say "I don't have enough information to answer this question."

Posts:
{context}

Question: {question}

Answer (include citation numbers like [1], [2] when referencing posts):"""
        
        try:
            if not self.llm_service.client:
                answer_text = "LLM service is not configured. Please configure OpenAI API key."
            else:
                answer = self.llm_service.client.chat.completions.create(
                    model=self.llm_service.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that answers questions based on provided posts. Always cite your sources using [number] format.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=500,
                    temperature=0.3,
                )
                
                answer_text = answer.choices[0].message.content.strip()
        except Exception as e:
            logger.error("Failed to generate answer", error=str(e))
            answer_text = "I encountered an error while generating an answer."
        
        return {
            "answer": answer_text,
            "citations": citations,
            "posts": posts,
        }

