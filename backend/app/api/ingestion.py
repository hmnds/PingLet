"""Ingestion endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.ingestion import IngestionService
from app.config import settings
from app.services.x_client import XClient, RealXClient, MockXClient
from app.api.deps import get_current_user

router = APIRouter(prefix="/ingest", tags=["ingestion"])


def get_x_client() -> XClient:
    """Dependency to get X client."""
    if not settings.x_api_bearer_token or settings.x_api_bearer_token == "your_x_api_bearer_token_here":
        return MockXClient()
    return RealXClient()


@router.post("/run")
def run_ingestion(
    db: Session = Depends(get_db),
    x_client: XClient = Depends(get_x_client),
    current_user = Depends(get_current_user),
):
    """Manually trigger ingestion for the current user's accounts."""
    service = IngestionService(x_client, db)
    result = service.ingest_user_accounts(current_user.id)
    return result



