"""Base notifier interface."""
from abc import ABC, abstractmethod
from typing import Dict, Any
from app.models import AlertRule, Post


class Notifier(ABC):
    """Abstract base class for notifiers."""

    @abstractmethod
    def send_alert(
        self,
        rule: AlertRule,
        post: Post,
        summary: str,
        trigger_info: Dict[str, Any],
    ) -> bool:
        """
        Send an alert notification.
        
        Args:
            rule: The alert rule that triggered
            post: The post that triggered the alert
            summary: 1-2 sentence summary of the post
            trigger_info: Additional info (trigger_type, score, etc.)
            
        Returns:
            True if sent successfully, False otherwise
        """
        pass

    @abstractmethod
    def send_digest(self, digest_content: str, digest_date: str) -> bool:
        """
        Send a daily digest.
        
        Args:
            digest_content: Markdown content of the digest
            digest_date: Date of the digest (YYYY-MM-DD)
            
        Returns:
            True if sent successfully, False otherwise
        """
        pass



