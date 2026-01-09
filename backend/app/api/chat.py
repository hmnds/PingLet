"""Chat endpoints."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.rag import RAGService
from app.services.embeddings import EmbeddingsService
from app.services.llm import LLMService
from app.models import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    question: str


def get_rag_service(db: Session = Depends(get_db)) -> RAGService:
    """Dependency to get RAG service."""
    embeddings_service = EmbeddingsService()
    llm_service = LLMService()
    return RAGService(db, embeddings_service, llm_service)


@router.post("")
def chat(
    request: ChatRequest,
    service: RAGService = Depends(get_rag_service),
    current_user: User = Depends(get_current_user),
):
    """Answer a question using RAG with citations based on user's monitored posts."""
    result = service.chat(request.question, user_id=current_user.id)
    return result



