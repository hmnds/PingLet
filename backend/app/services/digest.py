"""Daily digest generation service."""
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
import structlog
import numpy as np
from app.models import MonitoredAccount, Post, Digest, Topic
from app.services.llm import LLMService
from app.notifiers.base import Notifier

logger = structlog.get_logger()


class DigestService:
    """Service for generating daily digests."""

    def __init__(self, db: Session, llm_service: LLMService, notifier: Notifier):
        self.db = db
        self.llm_service = llm_service
        self.notifier = notifier

    def generate_digest(self, user_id: int, digest_date: Optional[date] = None, force: bool = False) -> Digest:
        """
        Generate a daily digest for the specified user and date (defaults to today).
        
        Args:
            user_id: ID of the user to generate digest for
            digest_date: Date to generate digest for (defaults to today)
            force: If True, regenerate digest even if it exists
            
        Returns:
            Digest object
        """
        if digest_date is None:
            digest_date = date.today()
        
        # Check if digest already exists for this user
        existing = self.db.query(Digest).filter(
            Digest.digest_date == digest_date,
            Digest.user_id == user_id
        ).order_by(Digest.created_at.desc()).first()
        
        if existing and not force:
             logger.info("Digest already exists for user (returning latest)", digest_date=digest_date, user_id=user_id)
             return existing
        
        if force:
             logger.info("Forcing generation of NEW digest", digest_date=digest_date, user_id=user_id)
             # We do NOT delete the old one, we create a new one.
             pass
        
        # Get posts from last 24h for digest_enabled accounts OWNED BY THIS USER
        start_time = datetime.combine(digest_date, datetime.min.time()) - timedelta(days=1)
        end_time = datetime.combine(digest_date, datetime.max.time())
        
        accounts = self.db.query(MonitoredAccount).filter(
            MonitoredAccount.digest_enabled == True,
            MonitoredAccount.user_id == user_id
        ).all()
        
        if not accounts:
            logger.info("No monitored accounts for user, skipping digest", user_id=user_id)
            # Create an empty digest so we don't keep retrying? Or just return None?
            # Creating empty digest is better for UI.
            digest = Digest(
                digest_date=digest_date,
                content_markdown="No accounts monitored or digest enabled.",
                user_id=user_id,
            )
            self.db.add(digest)
            self.db.commit()
            self.db.refresh(digest)
            return digest

        account_ids = [acc.id for acc in accounts]
        
        # Get user topics to filter by relevance
        topics = self.db.query(Topic).filter(Topic.user_id == user_id).all()
        
        posts = []
        stats_candidates = 0
        for account in accounts:
            # Base query
            query = self.db.query(Post).filter(
                Post.author_id == account.id,
            )
            
            # If user has topics, we only want posts that match ANY topic
            # However, doing this efficiently in SQL with many topics is tricky.
            # A common approach: If topics exist, fetch a bit more candidates (e.g. 20),
            # then filter in Python for best control or use a complex OR on cosine distances.
            # BUT, the user said "only select things related to topics IF set... of the 10 posts".
            # This implies: 
            # 1. Take the latest 10 posts (quota).
            # 2. If topics exist, filter those 10.
            # 3. If no topics, keep all 10.
            
            # Fetch latest 10 posts (quota includes reposts, assuming they are in DB)
            candidates = query.order_by(Post.created_at.desc()).limit(10).all()
            stats_candidates += len(candidates)
            
            if not topics:
                # No topics set -> General "what's on" (keep all)
                posts.extend(candidates)
            else:
                # Topics set -> Filter candidates by topic similarity
                relevant_candidates = []
                # Collect posts with their max similarity score
                scored_candidates = []
                
                for post in candidates:
                    if post.embedding is None:
                         continue
                         
                    # Safe embedding parsing
                    import json
                    raw_emb = post.embedding
                    if isinstance(raw_emb, str):
                         try:
                             raw_emb = json.loads(raw_emb)
                         except:
                             raw_emb = [float(x) for x in raw_emb.replace('[','').replace(']','').split(',')]

                    post_vec = np.array(raw_emb)
                    
                    max_similarity = -1.0
                    
                    for topic in topics:
                        if topic.embedding is None:
                            continue
                        
                        raw_topic_emb = topic.embedding
                        if isinstance(raw_topic_emb, str):
                             try:
                                 raw_topic_emb = json.loads(raw_topic_emb)
                             except:
                                 raw_topic_emb = [float(x) for x in raw_topic_emb.replace('[','').replace(']','').split(',')]

                        topic_vec = np.array(raw_topic_emb)
                        
                        # Dimension check
                        if post_vec.shape != topic_vec.shape:
                            continue

                        try:
                            similarity = np.dot(post_vec, topic_vec)
                            if similarity > max_similarity:
                                max_similarity = float(similarity)
                        except Exception:
                            continue
                    
                    if max_similarity > -1.0:
                        scored_candidates.append((post, max_similarity))
                
                # Logic:
                # 1. Try strict threshold
                # 2. If no results, try "soft" fallback (top 5 if score > 0.15)
                # 3. If all scores are 0 (likely missing API key), fallback to ALL
                
                # Default threshold from the first topic (or 0.7)
                threshold = topics[0].threshold if topics else 0.7
                
                relevant_candidates = [p for p, s in scored_candidates if s >= threshold]
                
                if not relevant_candidates:
                    # Check for "top matches" that missed threshold but aren't zero
                    # Filter for score > 0 (to avoid zero vectors)
                    non_zero_matches = [(p, s) for p, s in scored_candidates if s > 0.001]
                    
                    if non_zero_matches:
                        # We have some semantic signal, just weak. Take top 5.
                        non_zero_matches.sort(key=lambda x: x[1], reverse=True)
                        relevant_candidates = [p for p, s in non_zero_matches[:5]]
                        logger.info("Used soft fallback for topics", count=len(relevant_candidates))
                    else:
                        # All scores are 0 or below. Likely embeddings are zero vectors (missing API key).
                        # Fallback to ALL candidates to avoid empty digest.
                        logger.warning("All similarity scores are 0. Falling back to all posts.", user_id=user_id)
                        relevant_candidates = candidates
                
                
                posts.extend(relevant_candidates)
        
        logger.info(
            "Generating digest",
            digest_date=digest_date,
            user_id=user_id,
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
        if not posts:
             if stats_candidates > 0:
                 content = f"Analyzed {stats_candidates} recent posts from your accounts, but none matched your configured topics."
             else:
                 content = "No posts found for your monitored accounts today."
        else:
             content = self.llm_service.generate_digest(posts_by_author)
        
        # Store digest
        digest = Digest(
            digest_date=digest_date,
            content_markdown=content,
            user_id=user_id,
        )
        self.db.add(digest)
        self.db.commit()
        self.db.refresh(digest)
        
        # Send via notifier
        # TODO: Notifier might need user context (e.g. email address) if we support email
        try:
            self.notifier.send_digest(content, digest_date.isoformat())
        except Exception as e:
            logger.error("Failed to send digest", error=str(e), digest_id=digest.id)
        
        return digest



