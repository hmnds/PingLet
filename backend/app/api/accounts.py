"""Account CRUD endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import structlog
from app.database import get_db
from app.models import MonitoredAccount, User
from app.schemas import (
    MonitoredAccountCreate,
    MonitoredAccountUpdate,
    MonitoredAccountResponse,
)
from app.config import settings
from app.services.x_client import XClient, RealXClient, MockXClient
from app.api.deps import get_current_user

logger = structlog.get_logger()

router = APIRouter(prefix="/accounts", tags=["accounts"])


def get_x_client() -> XClient:
    """Dependency to get X client."""
    if not settings.x_api_bearer_token or settings.x_api_bearer_token == "your_x_api_bearer_token_here":
        logger.warning("Using MockXClient due to missing X API bearer token")
        return MockXClient()
    return RealXClient()


@router.post("", response_model=MonitoredAccountResponse, status_code=201)
def create_account(
    account: MonitoredAccountCreate,
    db: Session = Depends(get_db),
    x_client: XClient = Depends(get_x_client),
    current_user: User = Depends(get_current_user),
):
    """Create a new monitored account."""
    # Check if username already exists FOR THIS USER
    existing = db.query(MonitoredAccount).filter(
        MonitoredAccount.username == account.username,
        MonitoredAccount.user_id == current_user.id
    ).first()
    
    if existing:
         raise HTTPException(status_code=400, detail="You are already monitoring this account")
    
    # Resolve username to x_user_id
    try:
        logger.info("Attempting to resolve username", username=account.username)
        x_user_id = x_client.resolve_username(account.username)
        if not x_user_id:
            raise HTTPException(
                status_code=404, 
                detail=f"Username '{account.username}' not found on X. Please verify the username is correct."
            )
        logger.info("Successfully resolved username", username=account.username, x_user_id=x_user_id)
    except HTTPException:
        raise
    except Exception as e:
        # Return the actual error message
        logger.error("Error resolving username", username=account.username, error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    
    db_account = MonitoredAccount(
        username=account.username,
        x_user_id=x_user_id,
        digest_enabled=account.digest_enabled,
        alerts_enabled=account.alerts_enabled,
        user_id=current_user.id,
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    return db_account


@router.get("", response_model=List[MonitoredAccountResponse])
def list_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all monitored accounts for the current user."""
    accounts = db.query(MonitoredAccount).filter(MonitoredAccount.user_id == current_user.id).all()
    return accounts


@router.get("/{account_id}", response_model=MonitoredAccountResponse)
def get_account(
    account_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific monitored account."""
    account = db.query(MonitoredAccount).filter(
        MonitoredAccount.id == account_id,
        MonitoredAccount.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.patch("/{account_id}", response_model=MonitoredAccountResponse)
def update_account(
    account_id: int,
    update: MonitoredAccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a monitored account."""
    account = db.query(MonitoredAccount).filter(
        MonitoredAccount.id == account_id,
        MonitoredAccount.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Update only provided fields
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)
    
    db.commit()
    db.refresh(account)
    return account


@router.post("/{account_id}/resolve", response_model=MonitoredAccountResponse)
def resolve_account(
    account_id: int,
    db: Session = Depends(get_db),
    x_client: XClient = Depends(get_x_client),
    current_user: User = Depends(get_current_user),
):
    """Resolve username to x_user_id and update account."""
    account = db.query(MonitoredAccount).filter(
        MonitoredAccount.id == account_id,
        MonitoredAccount.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    try:
        logger.info("Attempting to resolve username", username=account.username)
        x_user_id = x_client.resolve_username(account.username)
        if not x_user_id:
            raise HTTPException(
                status_code=404, 
                detail=f"Username '{account.username}' not found on X. Please verify the username is correct."
            )
        logger.info("Successfully resolved username", username=account.username, x_user_id=x_user_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error resolving username", username=account.username, error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    
    account.x_user_id = x_user_id
    db.commit()
    db.refresh(account)
    return account


@router.delete("/{account_id}", status_code=204)
def delete_account(
    account_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a monitored account."""
    account = db.query(MonitoredAccount).filter(
        MonitoredAccount.id == account_id,
        MonitoredAccount.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    db.delete(account)
    db.commit()




