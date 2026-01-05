"""Daily digest generation service."""
from datetime import datetime, timedelta, date
from typing import Dict, List, Any
from sqlalchemy.orm import Session
import structlog
from app.models import MonitoredAccount, Post, Digest
from app.services.llm import LLMService
from app.notifiers.base import Notifier

logger = structlog.get_logger()


class DigestService:
    """Service for generating daily digests."""

    def __init__(self, db: Session, llm_service: LLMService, notifier: Notifier):
        self.db = db
        self.llm_service = llm_service
        self.notifier = notifier

    def generate_digest(self, digest_date: Optional[date] = None) -> Digest:
        """
        Generate a daily digest for the specified date (defaults to today).
        
        Args:
            digest_date: Date to generate digest for (defaults to today)
            
        Returns:
            Digest object
        """
        if digest_date is None:
            digest_date = date.today()
        
        # Check if digest already exists
        existing = self.db.query(Digest).filter(Digest.digest_date == digest_date).first()
        if existing:
            logger.info("Digest already exists", digest_date=digest_date)
            return existing
        
        # Get posts from last 24h for digest_enabled accounts
        start_time = datetime.combine(digest_date, datetime.min.time()) - timedelta(days=1)
        end_time = datetime.combine(digest_date, datetime.max.time())
        
        accounts = self.db.query(MonitoredAccount).filter(
            MonitoredAccount.digest_enabled == True
        ).all()
        
        account_ids = [acc.id for acc in accounts]
        
        posts = (
            self.db.query(Post)
            .filter(
                Post.author_id.in_(account_ids),
                Post.created_at >= start_time,
                Post.created_at <= end_time,
            )
            .order_by(Post.created_at.desc())
            .all()
        )
        
        logger.info(
            "Generating digest",
            digest_date=digest_date,
            accounts_count=len(accounts),
            posts_count=len(posts),
        )
        
        # Group posts by author
        posts_by_author: Dict[str, List[Dict[str, Any]]] = {}
        for post in posts:
            author = post.author.username
            if author not in posts_by_author:
                posts_by_author[author] = []
            
            posts_by_author[author].append({
                "text": post.text,
                "url": post.url,
                "created_at": post.created_at.isoformat(),
            })
        
        # Generate digest content
        content = self.llm_service.generate_digest(posts_by_author)
        
        # Store digest
        digest = Digest(
            digest_date=digest_date,
            content_markdown=content,
        )
        self.db.add(digest)
        self.db.commit()
        self.db.refresh(digest)
        
        # Send via notifier
        try:
            self.notifier.send_digest(content, digest_date.isoformat())
        except Exception as e:
            logger.error("Failed to send digest", error=str(e), digest_id=digest.id)
        
        return digest


