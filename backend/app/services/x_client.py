"""X API client interface and implementations."""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
import httpx
from app.schemas import XPost
from app.config import settings


class XClient(ABC):
    """Abstract base class for X API client."""

    @abstractmethod
    def resolve_username(self, username: str) -> Optional[str]:
        """
        Resolve username to x_user_id.
        
        Args:
            username: X username (without @)
            
        Returns:
            x_user_id if found, None otherwise
        """
        pass

    @abstractmethod
    def fetch_user_timeline(self, x_user_id: str, since_id: Optional[str] = None) -> List[XPost]:
        """
        Fetch user timeline posts.
        
        Args:
            x_user_id: X user ID
            since_id: Only fetch posts after this post ID (for delta fetching)
            
        Returns:
            List of posts, ordered by created_at descending
        """
        pass


class RealXClient(XClient):
    """Real X API client using httpx."""
    
    BASE_URL = "https://api.twitter.com/2"

    def __init__(self, bearer_token: Optional[str] = None):
        self.bearer_token = bearer_token or settings.x_api_bearer_token
        self.client = httpx.Client(
            headers={"Authorization": f"Bearer {self.bearer_token}"},
            timeout=30.0,
        )

    def resolve_username(self, username: str) -> Optional[str]:
        """Resolve username to x_user_id using X API v2."""
        try:
            # Remove @ if present
            username = username.lstrip("@")
            
            response = self.client.get(
                f"{self.BASE_URL}/users/by/username/{username}",
                params={"user.fields": "id"},
            )
            response.raise_for_status()
            data = response.json()
            
            if "data" in data and "id" in data["data"]:
                return data["data"]["id"]
            return None
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
        except Exception as e:
            raise Exception(f"Failed to resolve username: {e}")

    def fetch_user_timeline(self, x_user_id: str, since_id: Optional[str] = None) -> List[XPost]:
        """Fetch user timeline using X API v2."""
        try:
            params = {
                "max_results": 100,
                "tweet.fields": "created_at,text,author_id",
                "expansions": "author_id",
            }
            
            if since_id:
                params["since_id"] = since_id
            
            response = self.client.get(
                f"{self.BASE_URL}/users/{x_user_id}/tweets",
                params=params,
            )
            response.raise_for_status()
            data = response.json()
            
            posts = []
            if "data" in data:
                for tweet in data["data"]:
                    # Construct URL
                    url = f"https://twitter.com/i/web/status/{tweet['id']}"
                    
                    post = XPost(
                        id=tweet["id"],
                        text=tweet.get("text", ""),
                        created_at=datetime.fromisoformat(tweet["created_at"].replace("Z", "+00:00")),
                        author_id=tweet.get("author_id", x_user_id),
                        url=url,
                        raw_json=tweet,
                    )
                    posts.append(post)
            
            return posts
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return []
            raise
        except Exception as e:
            raise Exception(f"Failed to fetch timeline: {e}")

    def __del__(self):
        """Close httpx client on cleanup."""
        if hasattr(self, "client"):
            self.client.close()


class FakeXClient(XClient):
    """Fake X API client for testing with fixture data."""
    
    def __init__(self):
        # Fixture data
        self.users = {
            "elonmusk": "123456789",
            "jack": "987654321",
        }
        self.posts = {
            "123456789": [
                XPost(
                    id="1111111111111111111",
                    text="Test post from elonmusk",
                    created_at=datetime.utcnow(),
                    author_id="123456789",
                    url="https://twitter.com/i/web/status/1111111111111111111",
                    raw_json={"id": "1111111111111111111", "text": "Test post from elonmusk"},
                ),
            ],
            "987654321": [
                XPost(
                    id="2222222222222222222",
                    text="Test post from jack",
                    created_at=datetime.utcnow(),
                    author_id="987654321",
                    url="https://twitter.com/i/web/status/2222222222222222222",
                    raw_json={"id": "2222222222222222222", "text": "Test post from jack"},
                ),
            ],
        }

    def resolve_username(self, username: str) -> Optional[str]:
        """Resolve username to x_user_id from fixture data."""
        username = username.lstrip("@").lower()
        return self.users.get(username)

    def fetch_user_timeline(self, x_user_id: str, since_id: Optional[str] = None) -> List[XPost]:
        """Fetch user timeline from fixture data."""
        user_posts = self.posts.get(x_user_id, [])
        
        if since_id:
            # Filter posts after since_id
            filtered = []
            for post in user_posts:
                if post.id > since_id:
                    filtered.append(post)
            return filtered
        
        return user_posts


