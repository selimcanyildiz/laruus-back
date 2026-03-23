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
from app.services.email_service import generate_code, send_verification_email
from sqlalchemy import func


def register_user(db: Session, data: UserCreate) -> dict:
    existing_user = db.query(User).filter(User.email == data.email).first()

    if existing_user and existing_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    code = generate_code()

    if existing_user and not existing_user.is_verified:
        # Unverified user exists — update and resend code
        existing_user.first_name = data.first_name
        existing_user.last_name = data.last_name
        existing_user.phone = data.phone
        existing_user.password_hash = hash_password(data.password)
        existing_user.verification_code = code
        db.commit()
    else:
        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
            password_hash=hash_password(data.password),
            verification_code=code,
            is_verified=False,
        )
        db.add(user)
        db.commit()

    send_verification_email(data.email, code)
    return {"message": "Verification code sent", "email": data.email}


def verify_user(db: Session, email: str, code: str) -> str:
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified",
        )

    if user.verification_code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code",
        )

    user.is_verified = True
    user.verification_code = None
    db.commit()

    return create_access_token(subject=str(user.id))


def login_user(db: Session, data: UserLogin) -> str:
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_verified:
        # Resend verification code
        code = generate_code()
        user.verification_code = code
        db.commit()
        send_verification_email(data.email, code)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. A new code has been sent.",
        )

    user.last_login_at = func.now()
    db.commit()

    return create_access_token(subject=str(user.id))
