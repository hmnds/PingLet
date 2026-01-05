"""Pydantic schemas for API requests and responses."""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# Account schemas
class MonitoredAccountBase(BaseModel):
    username: str
    digest_enabled: bool = True
    alerts_enabled: bool = True


class MonitoredAccountCreate(MonitoredAccountBase):
    pass


class MonitoredAccountUpdate(BaseModel):
    digest_enabled: Optional[bool] = None
    alerts_enabled: Optional[bool] = None
    last_seen_post_id: Optional[str] = None


class MonitoredAccountResponse(MonitoredAccountBase):
    id: int
    x_user_id: Optional[str] = None
    last_seen_post_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Post schemas
class PostResponse(BaseModel):
    id: int
    x_post_id: str
    author_id: int
    created_at: datetime
    text: str
    url: Optional[str] = None
    stored_at: datetime

    class Config:
        from_attributes = True


# Topic schemas
class TopicBase(BaseModel):
    name: str
    description: str
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class TopicCreate(TopicBase):
    pass


class TopicResponse(TopicBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Alert Rule schemas
class AlertRuleBase(BaseModel):
    name: str
    enabled: bool = True
    keywords: Optional[List[str]] = None
    topic_ids: Optional[List[int]] = None
    allowed_author_ids: Optional[List[int]] = None
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    cooldown_minutes: int = Field(default=60, ge=0)
    channel: str = "log"


class AlertRuleCreate(AlertRuleBase):
    pass


class AlertRuleUpdate(BaseModel):
    enabled: Optional[bool] = None
    keywords: Optional[List[str]] = None
    topic_ids: Optional[List[int]] = None
    allowed_author_ids: Optional[List[int]] = None
    similarity_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    cooldown_minutes: Optional[int] = Field(None, ge=0)
    channel: Optional[str] = None


class AlertRuleResponse(AlertRuleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Alert Log schemas
class AlertLogResponse(BaseModel):
    id: int
    rule_id: int
    post_id: int
    trigger_type: str
    score: Optional[float] = None
    status: str
    sent_at: datetime

    class Config:
        from_attributes = True


# Digest schemas
class DigestResponse(BaseModel):
    id: int
    digest_date: date
    content_markdown: str
    created_at: datetime

    class Config:
        from_attributes = True


# X API response schemas (for internal use)
class XPost(BaseModel):
    """Represents a post from X API."""
    id: str
    text: str
    created_at: datetime
    author_id: str
    url: Optional[str] = None
    raw_json: Optional[Dict[str, Any]] = None


