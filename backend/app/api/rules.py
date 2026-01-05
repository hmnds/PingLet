"""Alert rule CRUD endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AlertRule
from app.schemas import (
    AlertRuleCreate,
    AlertRuleUpdate,
    AlertRuleResponse,
)

router = APIRouter(prefix="/rules", tags=["rules"])


@router.post("", response_model=AlertRuleResponse, status_code=201)
def create_rule(
    rule: AlertRuleCreate,
    db: Session = Depends(get_db),
):
    """Create a new alert rule."""
    # Check if name already exists
    existing = db.query(AlertRule).filter(AlertRule.name == rule.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Rule name already exists")
    
    db_rule = AlertRule(
        name=rule.name,
        enabled=rule.enabled,
        keywords=rule.keywords,
        topic_ids=rule.topic_ids,
        allowed_author_ids=rule.allowed_author_ids,
        similarity_threshold=rule.similarity_threshold,
        cooldown_minutes=rule.cooldown_minutes,
        channel=rule.channel,
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    
    return db_rule


@router.get("", response_model=List[AlertRuleResponse])
def list_rules(db: Session = Depends(get_db)):
    """List all alert rules."""
    rules = db.query(AlertRule).all()
    return rules


@router.get("/{rule_id}", response_model=AlertRuleResponse)
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    """Get a specific alert rule."""
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.patch("/{rule_id}", response_model=AlertRuleResponse)
def update_rule(
    rule_id: int,
    update: AlertRuleUpdate,
    db: Session = Depends(get_db),
):
    """Update an alert rule."""
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Update only provided fields
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)
    
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=204)
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete an alert rule."""
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db.delete(rule)
    db.commit()
    return None


