"""Alert log endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AlertLog, AlertRule, User
from app.schemas import AlertLogResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=List[AlertLogResponse])
def list_alerts(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    rule_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List alert logs for the current user."""
    query = db.query(AlertLog).join(AlertLog.rule).filter(AlertRule.user_id == current_user.id)
    
    if rule_id:
        query = query.filter(AlertLog.rule_id == rule_id)
    
    alerts = query.order_by(AlertLog.sent_at.desc()).offset(offset).limit(limit).all()
    return alerts



