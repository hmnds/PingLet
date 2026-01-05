"""Ingestion service for fetching and storing posts from X API."""
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import structlog
from app.models import MonitoredAccount, Post
from app.services.x_client import XClient
from app.schemas import XPost

logger = structlog.get_logger()


class IngestionService:
    """Service for ingesting posts from X API."""

    def __init__(self, x_client: XClient, db: Session):
        self.x_client = x_client
        self.db = db

    def ingest_all_accounts(self) -> dict:
        """
        Ingest new posts for all monitored accounts.
        
        Returns:
            dict with stats: accounts_processed, posts_fetched, posts_stored, errors
        """
        accounts = self.db.query(MonitoredAccount).all()
        stats = {
            "accounts_processed": 0,
            "posts_fetched": 0,
            "posts_stored": 0,
            "errors": [],
        }

        for account in accounts:
            try:
                result = self.ingest_account(account.id)
                stats["accounts_processed"] += 1
                stats["posts_fetched"] += result["posts_fetched"]
                stats["posts_stored"] += result["posts_stored"]
            except Exception as e:
                logger.error("Failed to ingest account", account_id=account.id, error=str(e))
                stats["errors"].append({"account_id": account.id, "error": str(e)})

        return stats

    def ingest_account(self, account_id: int) -> dict:
        """
        Ingest new posts for a specific account.
        
        Args:
            account_id: ID of the monitored account
            
        Returns:
            dict with stats: posts_fetched, posts_stored
        """
        account = self.db.query(MonitoredAccount).filter(MonitoredAccount.id == account_id).first()
        if not account:
            raise ValueError(f"Account {account_id} not found")

        if not account.x_user_id:
            logger.warning("Account has no x_user_id", account_id=account_id, username=account.username)
            return {"posts_fetched": 0, "posts_stored": 0}

        # Fetch new posts using delta fetching
        since_id = account.last_seen_post_id
        posts = self.x_client.fetch_user_timeline(account.x_user_id, since_id=since_id)
        
        logger.info(
            "Fetched posts from X API",
            account_id=account_id,
            username=account.username,
            posts_count=len(posts),
            since_id=since_id,
        )

        # Store new posts and dedupe
        stored_count = self._store_posts(posts, account_id)
        
        # Update last_seen_post_id if we got new posts
        if posts:
            # Posts are ordered by created_at descending, so first post has highest ID
            new_last_seen = posts[0].id
            account.last_seen_post_id = new_last_seen
            self.db.commit()
            logger.info(
                "Updated last_seen_post_id",
                account_id=account_id,
                last_seen_post_id=new_last_seen,
            )

        return {
            "posts_fetched": len(posts),
            "posts_stored": stored_count,
        }

    def _store_posts(self, posts: List[XPost], account_id: int) -> int:
        """
        Store posts in database with deduplication.
        
        Args:
            posts: List of XPost objects
            account_id: ID of the author account
            
        Returns:
            Number of posts actually stored (after deduplication)
        """
        stored_count = 0
        
        for post in posts:
            # Check if post already exists
            existing = (
                self.db.query(Post)
                .filter(Post.x_post_id == post.id)
                .first()
            )
            
            if existing:
                continue  # Skip duplicate
            
            # Create new post
            db_post = Post(
                x_post_id=post.id,
                author_id=account_id,
                created_at=post.created_at,
                text=post.text,
                url=post.url,
                raw_json=post.raw_json,
            )
            
            try:
                self.db.add(db_post)
                self.db.commit()
                stored_count += 1
            except IntegrityError:
                # Race condition: post was inserted by another process
                self.db.rollback()
                logger.warning("Post already exists (race condition)", x_post_id=post.id)
                continue
            except Exception as e:
                self.db.rollback()
                logger.error("Failed to store post", x_post_id=post.id, error=str(e))
                raise

        return stored_count


