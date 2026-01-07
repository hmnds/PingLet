"""Digest endpoints."""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Digest
from app.schemas import DigestResponse
from app.services.digest import DigestService
from app.services.llm import LLMService
from app.notifiers.log import LogNotifier

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
):
    """Manually trigger digest generation."""
    digest = service.generate_digest(digest_date)
    return digest


@router.get("/latest", response_model=DigestResponse)
def get_latest_digest(db: Session = Depends(get_db)):
    """Get the most recent digest."""
    digest = db.query(Digest).order_by(Digest.digest_date.desc()).first()
    if not digest:
        raise HTTPException(status_code=404, detail="No digests found")
    return digest


@router.get("/{digest_date}", response_model=DigestResponse)
def get_digest_by_date(digest_date: date, db: Session = Depends(get_db)):
    """Get digest by date."""
    digest = db.query(Digest).filter(Digest.digest_date == digest_date).first()
    if not digest:
        raise HTTPException(status_code=404, detail="Digest not found for this date")
    return digest



