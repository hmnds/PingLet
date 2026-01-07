"""Authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from typing import Optional

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"access_token": "fake-jwt-token", "token_type": "bearer", "user": {"email": new_user.email, "id": new_user.id}}

@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # In a real app, generate JWT token here
    # For now, simplistic return
    return {"access_token": "fake-jwt-token", "token_type": "bearer", "user": {"email": db_user.email, "id": db_user.id}}
@router.get("/me")
def me(db: Session = Depends(get_db)):
    # In real app, decode token and find user. 
    # For now, return first user or dummy.
    # We are using "fake-jwt-token" so we can't decode it. 
    # Just returning the latest user for demo.
    db_user = db.query(User).order_by(User.id.desc()).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"email": db_user.email, "id": db_user.id}
@router.post("/logout")
def logout():
    return {"message": "Logged out"}
