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
        Answer a question using RAG with citations.
        
        Args:
            question: User question
            user_id: User ID to filter posts by
            limit: Maximum number of posts to retrieve
            
        Returns:
            Dict with answer, citations, and retrieved posts
        """
        # Search for relevant posts within user's scope
        raw_posts = self.search(question, user_id, limit=limit)
        
        # Filter posts by relevance threshold to correctly handle "normal LLM" mode
        # If query is "hi", dot product with trading posts will be low.
        RELEVANCE_THRESHOLD = 0.35
        posts = [p for p in raw_posts if p.get('similarity', 0) > RELEVANCE_THRESHOLD]
        
        # If no relevant posts found, we proceed with empty context
        # This effectively makes it a "normal LLM" for irrelevant queries
        
        # Build context from retrieved posts
        context_parts = []
        citations = []
        
        if posts:
            for i, post in enumerate(posts, 1):
                context_parts.append(f"[{i}] {post['text']}")
                if post['url']:
                    citations.append({
                        "index": i,
                        "url": post['url'],
                        "text_preview": post['text'][:100] + "..." if len(post['text']) > 100 else post['text'],
                    })
            context = "\n\n".join(context_parts)
        else:
            context = "No relevant posts found."

                # Generate answer with citations
        prompt = f"""You are an Expert Crypto/Stock Trading Analyst who is also a helpful assistant.
        
Your goal is to answer the user's question based on the social media posts below.

**MODE 1: TRADE STRATEGY**
If the user explicitly asks for a "strategy", "signal", "trade idea", or specific financial advice about a ticker (e.g., "Trade strategy for BTC", "Should I buy SOL?"), you MUST output a structured analysis in this format:

## Trade Strategy: [TICKER]
**Signal:** [LONG/SHORT/NEUTRAL]
**Confidence:** [High/Medium/Low]

*   **Entry Zone:** [Price or "Current Market Price"]
*   **Target (TP):** [Price or "Open"]
*   **Stop Loss (SL):** [Price or "N/A"]

### Rationale
[Brief explanation citing specific posts using [1], [2] format.]

---
**Disclaimer:** This is an AI-generated analysis based on social sentiment, not financial advice.

**MODE 2: GENERAL CHAT**
If the user asks a general question (e.g., "What are people saying about AI?", "Summarize the news", "Who is posting?"), simply answer the question clearly and concisely, citing sources with [1], [2], etc. Do NOT use the Trade Strategy format for general questions.

**Posts:**
{context}

**User Question:** {question}

**Answer:**"""
        
        try:
            if not self.llm_service.client:
                answer_text = "LLM service is not configured. Please configure OpenAI API key."
            else:
                answer = self.llm_service.client.chat.completions.create(
                    model=self.llm_service.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a senior financial analyst. You strictly follow the requested Markdown format. You do not hallucinate signals.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=800,
                    temperature=0.2,
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

