"""Digest endpoints."""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Digest, User
from app.schemas import DigestResponse
from app.services.digest import DigestService
from app.services.llm import LLMService
from app.notifiers.log import LogNotifier
from app.services.ingestion import IngestionService
from app.services.x_client import XClient
from app.api.deps import get_current_user, get_x_client

router = APIRouter(prefix="/digests", tags=["digests"])


def get_digest_service(db: Session = Depends(get_db)) -> DigestService:
    """Dependency to get digest service."""
    llm_service = LLMService()
    notifier = LogNotifier()
    return DigestService(db, llm_service, notifier)


@router.post("/run")
def run_digest(
    digest_date: Optional[date] = None,
    service: DigestService = Depends(get_digest_service),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    x_client: XClient = Depends(get_x_client),
):
    """Manually trigger ingestion AND digest generation for the current user."""
    try:
        # First, run ingestion to get latest posts
        ingestion_service = IngestionService(x_client, db)
        stats = ingestion_service.ingest_user_accounts(current_user.id)
        
        import structlog
        logger = structlog.get_logger()
        logger.info("Manual digest trigger stats", user_id=current_user.id, stats=stats)
        
        # Then generate digest
        digest = service.generate_digest(user_id=current_user.id, digest_date=digest_date, force=True)
        return digest
    except Exception as e:
        logger.error("Failed to run digest", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate digest: {str(e)}")


@router.get("/latest", response_model=DigestResponse)
def get_latest_digest(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the most recent digest for the current user."""
    digest = db.query(Digest).filter(Digest.user_id == current_user.id).order_by(Digest.created_at.desc()).first()
    if not digest:
        raise HTTPException(status_code=404, detail="No digests found")
    return digest


@router.get("/{digest_date}", response_model=DigestResponse)
def get_digest_by_date(
    digest_date: date, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get digest by date for the current user."""
    digest = db.query(Digest).filter(
        Digest.digest_date == digest_date,
        Digest.user_id == current_user.id
    ).order_by(Digest.created_at.desc()).first()
    if not digest:
        raise HTTPException(status_code=404, detail="Digest not found for this date")
    return digest
@router.get("/", response_model=list[DigestResponse])
def list_digests(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all digests for the current user."""
    digests = (
        db.query(Digest)
        .filter(Digest.user_id == current_user.id)
        .order_by(Digest.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return digests
