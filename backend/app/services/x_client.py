"""X API client interface and implementations."""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
import httpx
import structlog
from app.schemas import XPost
from app.config import settings

logger = structlog.get_logger()


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
            
            # Check if bearer token is configured
            if not self.bearer_token or self.bearer_token == "your_x_api_bearer_token_here":
                logger.error("X API bearer token not configured")
                raise Exception("X API bearer token is not configured. Please set X_API_BEARER_TOKEN in .env file")
            
            logger.info("Resolving username", username=username)
            
            response = self.client.get(
                f"{self.BASE_URL}/users/by/username/{username}",
                params={"user.fields": "id"},
            )
            
            # Log response for debugging
            logger.debug(
                "X API response",
                status_code=response.status_code,
                url=str(response.url)
            )
            
            response.raise_for_status()
            data = response.json()
            
            if "data" in data and "id" in data["data"]:
                user_id = data["data"]["id"]
                logger.info("Successfully resolved username", username=username, user_id=user_id)
                return user_id
            return None
        except httpx.HTTPStatusError as e:
            # Get detailed error message from X API
            error_detail = f"Status {e.response.status_code}"
            error_full_response = None
            try:
                error_data = e.response.json()
                error_full_response = error_data
                if "errors" in error_data:
                    error_messages = [err.get("message", "") for err in error_data["errors"]]
                    error_codes = [str(err.get("code", "")) for err in error_data["errors"]]
                    error_detail = "; ".join(error_messages)
                    if error_codes:
                        error_detail += f" (codes: {', '.join(error_codes)})"
                elif "detail" in error_data:
                    error_detail = error_data["detail"]
                elif "title" in error_data:
                    error_detail = error_data["title"]
            except (ValueError, KeyError):
                try:
                    error_detail = (
                        e.response.text[:500] 
                        if hasattr(e.response, 'text') 
                        else str(e)
                    )
                except (AttributeError, Exception):
                    error_detail = str(e)
            
            # Log full error response for debugging
            logger.error(
                "X API full error response",
                status_code=e.response.status_code,
                error_response=error_full_response or e.response.text[:500] if hasattr(e.response, 'text') else None
            )
            
            logger.error(
                "X API error resolving username",
                username=username,
                status_code=e.response.status_code,
                error=error_detail
            )
            
            if e.response.status_code == 401:
                raise Exception(
                    f"X API authentication failed (401): {error_detail}. "
                    "Your bearer token is invalid or expired. "
                    "Please get a new token from https://developer.x.com/en/portal/dashboard "
                    "and update X_API_BEARER_TOKEN in your .env file."
                )
            elif e.response.status_code == 403:
                raise Exception(f"X API access forbidden (403): {error_detail}. Check your API permissions.")
            elif e.response.status_code == 404:
                return None
            elif e.response.status_code == 429:
                raise Exception(f"X API rate limit exceeded (429): {error_detail}. Please wait and try again.")
            else:
                raise Exception(f"X API error ({e.response.status_code}): {error_detail}")
        except Exception as e:
            logger.error("Failed to resolve username", username=username, error=str(e))
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


class MockXClient(XClient):
    """Mock X API client for testing/development."""

    def resolve_username(self, username: str) -> Optional[str]:
        """Resolve username to dummy x_user_id."""
        logger.info("Mock resolving username", username=username)
        # Generate a deterministic dummy ID based on username
        return f"mock_{abs(hash(username))}"

    def fetch_user_timeline(self, x_user_id: str, since_id: Optional[str] = None) -> List[XPost]:
        """Fetch dummy user timeline."""
        logger.info("Mock fetching timeline", x_user_id=x_user_id)
        now = datetime.now()
        return [
            XPost(
                id=f"mock_msg_{i}_{x_user_id}",
                text=f"This is a mock tweet {i} from user {x_user_id}. #testing",
                created_at=now,
                author_id=x_user_id,
                url=f"https://twitter.com/mock/status/{i}",
                raw_json={"mock": True}
            ) for i in range(1, 4)
        ]





