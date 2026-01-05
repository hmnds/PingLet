"""Ingestion endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.ingestion import IngestionService
from app.services.x_client import XClient, RealXClient

router = APIRouter(prefix="/ingest", tags=["ingestion"])


def get_x_client() -> XClient:
    """Dependency to get X client."""
    return RealXClient()


@router.post("/run")
def run_ingestion(
    db: Session = Depends(get_db),
    x_client: XClient = Depends(get_x_client),
):
    """Manually trigger ingestion for all accounts."""
    service = IngestionService(x_client, db)
    result = service.ingest_all_accounts()
    return result


