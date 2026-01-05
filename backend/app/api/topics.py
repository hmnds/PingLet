"""Topic CRUD endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Topic
from app.schemas import TopicCreate, TopicResponse
from app.services.embeddings import EmbeddingsService

router = APIRouter(prefix="/topics", tags=["topics"])


def get_embeddings_service() -> EmbeddingsService:
    """Dependency to get embeddings service."""
    return EmbeddingsService()


@router.post("", response_model=TopicResponse, status_code=201)
def create_topic(
    topic: TopicCreate,
    db: Session = Depends(get_db),
    embeddings_service: EmbeddingsService = Depends(get_embeddings_service),
):
    """Create a new topic with embedding."""
    # Check if name already exists
    existing = db.query(Topic).filter(Topic.name == topic.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Topic name already exists")
    
    # Generate embedding for topic description
    embedding = embeddings_service.embed_text(topic.description)
    
    db_topic = Topic(
        name=topic.name,
        description=topic.description,
        threshold=topic.threshold,
        embedding=embedding,
    )
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    
    return db_topic


@router.get("", response_model=List[TopicResponse])
def list_topics(db: Session = Depends(get_db)):
    """List all topics."""
    topics = db.query(Topic).all()
    return topics


@router.get("/{topic_id}", response_model=TopicResponse)
def get_topic(topic_id: int, db: Session = Depends(get_db)):
    """Get a specific topic."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


@router.delete("/{topic_id}", status_code=204)
def delete_topic(topic_id: int, db: Session = Depends(get_db)):
    """Delete a topic."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    db.delete(topic)
    db.commit()
    return None


