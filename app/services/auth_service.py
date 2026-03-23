# app/services/auth_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from sqlalchemy import func


def register_user(db: Session, data: UserCreate) -> str:
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone=data.phone,
        password_hash=hash_password(data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return create_access_token(subject=str(user.id))


def login_user(db: Session, data: UserLogin) -> str:
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # 🔥 last_login_at güncelle
    user.last_login_at = func.now()
    db.commit()

    return create_access_token(subject=str(user.id))
