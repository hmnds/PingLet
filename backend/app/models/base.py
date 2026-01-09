"""SQLAlchemy models for PingLet."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Date, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from app.database import Base


from sqlalchemy import UniqueConstraint

class MonitoredAccount(Base):
    """Monitored X (Twitter) account."""
    __tablename__ = "monitored_accounts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False, unique=False, index=True)
    x_user_id = Column(String(255), nullable=True, index=True)
    digest_enabled = Column(Boolean, default=True, nullable=False)
    alerts_enabled = Column(Boolean, default=True, nullable=False)
    last_seen_post_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="monitored_accounts")
    posts = relationship("Post", back_populates="author")

    __table_args__ = (
        UniqueConstraint('user_id', 'username', name='uix_user_username'),
    )


class Post(Base):
    """X (Twitter) post."""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    x_post_id = Column(String(255), nullable=False, unique=False, index=True)
    author_id = Column(Integer, ForeignKey("monitored_accounts.id"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, index=True)
    text = Column(Text, nullable=False)
    url = Column(String(512), nullable=True)
    raw_json = Column(JSONB, nullable=True)
    embedding = Column(Vector(1536), nullable=True)  # OpenAI text-embedding-3-small dimension
    stored_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    author = relationship("MonitoredAccount", back_populates="posts")
    alert_logs = relationship("AlertLog", back_populates="post")

    __table_args__ = (
        UniqueConstraint('author_id', 'x_post_id', name='uix_author_xpostid'),
    )


class Topic(Base):
    """Topic for semantic matching."""
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, unique=False, index=True)
    description = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=True)
    threshold = Column(Float, default=0.7, nullable=False)  # Cosine similarity threshold
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="topics")


class AlertRule(Base):
    """Alert rule for keyword/topic matching."""
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, unique=False, index=True)
    enabled = Column(Boolean, default=True, nullable=False)
    keywords = Column(JSON, nullable=True)  # List of strings
    topic_ids = Column(JSON, nullable=True)  # List of topic IDs
    allowed_author_ids = Column(JSON, nullable=True)  # List of author IDs (allowlist)
    similarity_threshold = Column(Float, default=0.7, nullable=False)
    cooldown_minutes = Column(Integer, default=60, nullable=False)
    channel = Column(String(50), default="log", nullable=False)  # log, email, telegram, webhook
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="alert_rules")
    alert_logs = relationship("AlertLog", back_populates="rule")


class AlertLog(Base):
    """Log of triggered alerts."""
    __tablename__ = "alerts_log"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("alert_rules.id"), nullable=False, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    trigger_type = Column(String(50), nullable=False)  # keyword, topic
    score = Column(Float, nullable=True)  # Similarity score for topic matches
    status = Column(String(50), default="sent", nullable=False)  # sent, failed
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    rule = relationship("AlertRule", back_populates="alert_logs")
    post = relationship("Post", back_populates="alert_logs")


class Digest(Base):
    """Daily digest."""
    __tablename__ = "digests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    digest_date = Column(Date, nullable=False, unique=False, index=True)
    content_markdown = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="digests")


class Setting(Base):
    """Application settings (multi-tenant)."""
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    key = Column(String(255), nullable=False, unique=False, index=True)
    value = Column(JSON, nullable=False)  # Can store any JSON value
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="settings")


