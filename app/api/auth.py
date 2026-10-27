"""Authentication routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import schemas
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.entities import User
from app.repositories import users as user_repo
from app.services.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut, status_code=201)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    if user_repo.get_by_email(db, payload.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    return user_repo.create_user(db, payload.email, payload.password, payload.full_name)


@router.post("/login", response_model=schemas.Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = user_repo.get_by_email(db, form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    return schemas.Token(access_token=create_access_token(user.email))


@router.get("/me", response_model=schemas.UserOut)
def me(current: User = Depends(get_current_user)):
    return current