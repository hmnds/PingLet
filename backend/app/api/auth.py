"""Authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from typing import Optional
from app.api.deps import get_current_user
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user_by_name = db.query(User).filter(User.username == user.username).first()
    if db_user_by_name:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_password = pwd_context.hash(user.password)
    new_user = User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = create_access_token(new_user.id)
    return {"access_token": token, "token_type": "bearer", "user": {"email": new_user.email, "username": new_user.username, "id": new_user.id}}

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(db_user.id)
    return {"access_token": token, "token_type": "bearer", "user": {"email": db_user.email, "username": db_user.username, "id": db_user.id}}

@router.get("/me")
# Use dependency to get current user instead of dummy logic
def me(current_user: User = Depends(get_current_user)):
    return {"email": current_user.email, "username": current_user.username, "id": current_user.id}
@router.post("/logout")
def logout():
    return {"message": "Logged out"}
