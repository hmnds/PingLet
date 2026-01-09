"""Search endpoints."""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.rag import RAGService
from app.services.embeddings import EmbeddingsService
from app.services.llm import LLMService
from app.models import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/search", tags=["search"])


def get_rag_service(db: Session = Depends(get_db)) -> RAGService:
    """Dependency to get RAG service."""
    embeddings_service = EmbeddingsService()
    llm_service = LLMService()
    return RAGService(db, embeddings_service, llm_service)


@router.post("")
def search_posts(
    query: str = Query(..., description="Search query"),
    limit: int = Query(default=10, ge=1, le=50),
    service: RAGService = Depends(get_rag_service),
    current_user: User = Depends(get_current_user),
):
    """Search posts using vector similarity for the current user."""
    results = service.search(query, user_id=current_user.id, limit=limit)
    return {"query": query, "results": results}



