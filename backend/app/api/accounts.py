"""Account CRUD endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import MonitoredAccount
from app.schemas import (
    MonitoredAccountCreate,
    MonitoredAccountUpdate,
    MonitoredAccountResponse,
)
from app.services.x_client import XClient, RealXClient

router = APIRouter(prefix="/accounts", tags=["accounts"])


def get_x_client() -> XClient:
    """Dependency to get X client (can be swapped for FakeXClient in tests)."""
    return RealXClient()


@router.post("", response_model=MonitoredAccountResponse, status_code=201)
def create_account(
    account: MonitoredAccountCreate,
    db: Session = Depends(get_db),
    x_client: XClient = Depends(get_x_client),
):
    """Create a new monitored account."""
    # Check if username already exists
    existing = db.query(MonitoredAccount).filter(MonitoredAccount.username == account.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Resolve username to x_user_id
    x_user_id = x_client.resolve_username(account.username)
    if not x_user_id:
        raise HTTPException(status_code=404, detail="Username not found on X")
    
    db_account = MonitoredAccount(
        username=account.username,
        x_user_id=x_user_id,
        digest_enabled=account.digest_enabled,
        alerts_enabled=account.alerts_enabled,
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    return db_account


@router.get("", response_model=List[MonitoredAccountResponse])
def list_accounts(db: Session = Depends(get_db)):
    """List all monitored accounts."""
    accounts = db.query(MonitoredAccount).all()
    return accounts


@router.get("/{account_id}", response_model=MonitoredAccountResponse)
def get_account(account_id: int, db: Session = Depends(get_db)):
    """Get a specific monitored account."""
    account = db.query(MonitoredAccount).filter(MonitoredAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.patch("/{account_id}", response_model=MonitoredAccountResponse)
def update_account(
    account_id: int,
    update: MonitoredAccountUpdate,
    db: Session = Depends(get_db),
):
    """Update a monitored account."""
    account = db.query(MonitoredAccount).filter(MonitoredAccount.id == account_id).first()
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
):
    """Resolve username to x_user_id and update account."""
    account = db.query(MonitoredAccount).filter(MonitoredAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    x_user_id = x_client.resolve_username(account.username)
    if not x_user_id:
        raise HTTPException(status_code=404, detail="Username not found on X")
    
    account.x_user_id = x_user_id
    db.commit()
    db.refresh(account)
    return account


