"""Log notifier implementation."""
import structlog
from typing import Dict, Any
from app.models import AlertRule, Post
from app.notifiers.base import Notifier

logger = structlog.get_logger()


class LogNotifier(Notifier):
    """Notifier that writes to structured logs."""

    def send_alert(
        self,
        rule: AlertRule,
        post: Post,
        summary: str,
        trigger_info: Dict[str, Any],
    ) -> bool:
        """Send alert to log."""
        logger.info(
            "ALERT",
            rule_id=rule.id,
            rule_name=rule.name,
            post_id=post.id,
            post_url=post.url,
            author_id=post.author_id,
            summary=summary,
            trigger_type=trigger_info.get("trigger_type"),
            score=trigger_info.get("score"),
        )
        return True

    def send_digest(self, digest_content: str, digest_date: str) -> bool:
        """Send digest to log."""
        logger.info(
            "DIGEST",
            digest_date=digest_date,
            content_length=len(digest_content),
            content_preview=digest_content[:200] + "..." if len(digest_content) > 200 else digest_content,
        )
        return True



