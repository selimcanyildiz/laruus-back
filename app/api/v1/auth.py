from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_db
from app.schemas.user import UserCreate, UserLogin, Token
from app.services.auth_service import register_user, login_user, verify_user
from app.core.security import get_current_user_id
from app.db.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])


class VerifyRequest(BaseModel):
    email: str
    code: str


@router.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    result = register_user(db, data)
    return result


@router.post("/verify", response_model=Token)
def verify(data: VerifyRequest, db: Session = Depends(get_db)):
    token = verify_user(db, data.email, data.code)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    token = login_user(db, data)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def me(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": str(user.id),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": user.phone,
        "is_admin": user.is_admin,
        "created_at": user.created_at,
        "last_login_at": user.last_login_at,
    }
