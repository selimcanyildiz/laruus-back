from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_db
from app.schemas.user import UserCreate, UserLogin, Token
from app.services.auth_service import register_user, login_user, verify_user

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
