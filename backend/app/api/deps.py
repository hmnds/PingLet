from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

from jose import jwt, JWTError
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Get current user from JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Check for fake token first during transition (optional, can remove later)
        if token.startswith("fake-jwt-token-"):
            user_id = int(token.split("-")[-1])
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                return user
            raise credentials_exception

        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user

from app.services.x_client import XClient, RealXClient, MockXClient

def get_x_client() -> XClient:
    """Dependency to get X client."""
    if not settings.x_api_bearer_token or settings.x_api_bearer_token == "your_x_api_bearer_token_here":
        return MockXClient()
    return RealXClient()
