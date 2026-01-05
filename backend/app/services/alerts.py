"""Alert matching engine."""
import re
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import structlog
import numpy as np
from app.models import AlertRule, Post, AlertLog, MonitoredAccount, Topic
from app.services.embeddings import EmbeddingsService
from app.services.llm import LLMService
from app.notifiers.base import Notifier

logger = structlog.get_logger()


class AlertEngine:
    """Engine for matching posts against alert rules."""

    def __init__(self, db: Session, embeddings_service: EmbeddingsService, llm_service: LLMService, notifier: Notifier):
        self.db = db
        self.embeddings_service = embeddings_service
        self.llm_service = llm_service
        self.notifier = notifier

    def check_post(self, post: Post) -> List[Dict[str, Any]]:
        """
        Check a post against all enabled alert rules.
        
        Args:
            post: Post to check
            
        Returns:
            List of triggered alert info dicts
        """
        # Get all enabled rules
        rules = self.db.query(AlertRule).filter(AlertRule.enabled == True).all()
        
        triggered = []
        for rule in rules:
            result = self._check_rule(post, rule)
            if result:
                triggered.append(result)
        
        return triggered

    def _check_rule(self, post: Post, rule: AlertRule) -> Optional[Dict[str, Any]]:
        """
        Check a post against a specific rule.
        
        Returns:
            Dict with alert info if triggered, None otherwise
        """
        # Check author allowlist
        if rule.allowed_author_ids:
            if post.author_id not in rule.allowed_author_ids:
                return None
        
        # Check cooldown
        if self._is_in_cooldown(rule, post):
            return None
        
        # Check keyword matching
        keyword_match = self._check_keywords(post, rule)
        if keyword_match:
            return self._trigger_alert(post, rule, "keyword", None)
        
        # Check topic matching
        topic_match = self._check_topics(post, rule)
        if topic_match:
            return self._trigger_alert(post, rule, "topic", topic_match["score"])
        
        return None

    def _check_keywords(self, post: Post, rule: AlertRule) -> bool:
        """Check if post matches any keywords in the rule."""
        if not rule.keywords:
            return False
        
        post_text_lower = post.text.lower()
        
        for keyword in rule.keywords:
            # Simple case-insensitive substring match
            # TODO: Add regex support later
            if keyword.lower() in post_text_lower:
                return True
        
        return False

    def _check_topics(self, post: Post, rule: AlertRule) -> Optional[Dict[str, float]]:
        """
        Check if post matches any topics in the rule using cosine similarity.
        
        Returns:
            Dict with "score" if match found, None otherwise
        """
        if not rule.topic_ids:
            return None
        
        # Get post embedding (generate if missing)
        if not post.embedding:
            embedding = self.embeddings_service.embed_text(post.text)
            if embedding:
                post.embedding = embedding
                self.db.commit()
        
        if not post.embedding:
            return None
        
        # Get topics
        topics = self.db.query(Topic).filter(Topic.id.in_(rule.topic_ids)).all()
        
        best_score = 0.0
        for topic in topics:
            if not topic.embedding:
                continue
            
            # Compute cosine similarity
            similarity = self._cosine_similarity(post.embedding, topic.embedding)
            
            # Check if similarity exceeds both topic threshold and rule threshold
            if similarity >= topic.threshold and similarity >= rule.similarity_threshold:
                if similarity > best_score:
                    best_score = similarity
        
        if best_score > 0:
            return {"score": best_score}
        
        return None

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            
            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
        except Exception as e:
            logger.error("Failed to compute cosine similarity", error=str(e))
            return 0.0

    def _is_in_cooldown(self, rule: AlertRule, post: Post) -> bool:
        """Check if rule is in cooldown period for this post's author."""
        if rule.cooldown_minutes <= 0:
            return False
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=rule.cooldown_minutes)
        
        # Check if there's a recent alert for this rule and author
        recent_alert = (
            self.db.query(AlertLog)
            .join(Post)
            .filter(
                AlertLog.rule_id == rule.id,
                Post.author_id == post.author_id,
                AlertLog.sent_at >= cutoff_time,
            )
            .first()
        )
        
        return recent_alert is not None

    def _trigger_alert(
        self,
        post: Post,
        rule: AlertRule,
        trigger_type: str,
        score: Optional[float],
    ) -> Dict[str, Any]:
        """Trigger an alert and send notification."""
        # Generate summary via LLM (will be implemented in step 9, stub for now)
        summary = self._generate_summary(post)
        
        # Create alert log entry
        alert_log = AlertLog(
            rule_id=rule.id,
            post_id=post.id,
            trigger_type=trigger_type,
            score=score,
            status="sent",
        )
        self.db.add(alert_log)
        
        # Send notification
        trigger_info = {
            "trigger_type": trigger_type,
            "score": score,
        }
        
        try:
            success = self.notifier.send_alert(rule, post, summary, trigger_info)
            if not success:
                alert_log.status = "failed"
        except Exception as e:
            logger.error("Failed to send alert", error=str(e), rule_id=rule.id, post_id=post.id)
            alert_log.status = "failed"
        
        self.db.commit()
        
        return {
            "rule_id": rule.id,
            "post_id": post.id,
            "trigger_type": trigger_type,
            "score": score,
            "summary": summary,
        }

    def _generate_summary(self, post: Post) -> str:
        """Generate a 1-2 sentence summary of the post."""
        return self.llm_service.generate_summary(post.text, max_sentences=2)

