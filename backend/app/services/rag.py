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
        
        # Use CAST() syntax which is safer with SQLAlchemy text() than :: operator
        sql = text("""
            SELECT 
                p.id, p.x_post_id, p.author_id, p.created_at, p.text, p.url,
                1 - (p.embedding <=> CAST(:query_embedding AS vector)) as similarity
            FROM posts p
            JOIN monitored_accounts m ON p.author_id = m.id
            WHERE p.embedding IS NOT NULL AND m.user_id = :user_id
            ORDER BY p.embedding <=> CAST(:query_embedding AS vector)
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
        Answer a question using RAG with citations via LangGraph agent.
        
        Args:
            question: User question
            user_id: User ID to filter posts by
            limit: Maximum number of posts to retrieve
            
        Returns:
            Dict with answer, citations, and retrieved posts
        """
        from app.services.rag_agent import RAGAgent
        
        def search_func(query, uid, limit=10):
            return self.search(query, uid, limit=limit)
            
        agent = RAGAgent(search_func, user_id)
        answer_text = agent.invoke(question)
        
        posts = getattr(agent, "used_posts", [])
        
        unique_posts = []
        seen_ids = set()
        for p in posts:
            if p['id'] not in seen_ids:
                seen_ids.add(p['id'])
                unique_posts.append(p)
                
        citations = []
        if unique_posts:
            for i, post in enumerate(unique_posts, 1):
                if post['url']:
                    citations.append({
                        "index": i,
                        "url": post['url'],
                        "text_preview": post['text'][:100] + "..." if len(post['text']) > 100 else post['text'],
                    })
                    
        return {
            "answer": answer_text,
            "citations": citations,
            "posts": unique_posts,
        }
