"""Ingestion service for fetching and storing posts from X API."""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import structlog
from app.models import MonitoredAccount, Post
from app.services.x_client import XClient
from app.schemas import XPost

logger = structlog.get_logger()


from app.services.embeddings import EmbeddingsService

class IngestionService:
    """Service for ingesting posts from X API."""

    def __init__(self, x_client: XClient, db: Session, embeddings_service: Optional[EmbeddingsService] = None):
        self.x_client = x_client
        self.db = db
        self.embeddings_service = embeddings_service or EmbeddingsService()

    # ... (ingest_all_accounts and ingest_account remain same)

    def _store_posts(self, posts: List[XPost], account_id: int) -> int:
        """Store posts in database with deduplication."""
        stored_count = 0
        
        # Prepare batch texts for embedding if service is available
        if self.embeddings_service:
            # Only embed posts that we are about to store (checking duplicates first would be better efficiency but harder to batch)
            # For simplicity, we'll embed one by one or we could filter first. 
            # Let's filter duplicates first in memory using existing DB check
            pass

        for post in posts:
            # Check if post already exists
            existing = (
                self.db.query(Post)
                .filter(Post.x_post_id == post.id)
                .first()
            )
            
            if existing:
                continue  # Skip duplicate
            
            # Generate embedding
            embedding = None
            if self.embeddings_service:
                try:
                    embedding = self.embeddings_service.embed_text(post.text)
                except Exception as e:
                    logger.error("Failed to generate embedding during ingestion", error=str(e))

            # Create new post
            db_post = Post(
                x_post_id=post.id,
                author_id=account_id,
                created_at=post.created_at,
                text=post.text,
                url=post.url,
                raw_json=post.raw_json,
                embedding=embedding,
            )
            
            try:
                self.db.add(db_post)
                self.db.commit()
                stored_count += 1
            except IntegrityError:
                self.db.rollback()
                logger.warning("Post already exists (race condition)", x_post_id=post.id)
                continue
            except Exception as e:
                self.db.rollback()
                logger.error("Failed to store post", x_post_id=post.id, error=str(e))
                raise

        return stored_count

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

from typing import List, Optional



