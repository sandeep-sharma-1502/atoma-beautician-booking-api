from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse
from app.services import auth_service
from app.core.exceptions import UnauthorizedException

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(deps.get_db)):
    """Register a new user (Customer or Beautician)."""
    user = await auth_service.create_user(db, user_in=user_in)
    return user

@router.post("/token", response_model=Token)
async def login_access_token(db: AsyncSession = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 compatible token login, get an access token for future requests."""
    user = await auth_service.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise UnauthorizedException(detail="Incorrect email or password")
    elif not user.is_active:
        raise UnauthorizedException(detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email, expires_delta=access_token_expires, role=user.role.value
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
