from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.config import settings
from app.models.user import User, UserRole
from app.services.auth_service import get_user_by_email
from app.core.exceptions import UnauthorizedException, ForbiddenException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise UnauthorizedException(detail="Could not validate credentials")
    except JWTError:
        raise UnauthorizedException(detail="Could not validate credentials")
        
    user = await get_user_by_email(db, email=email)
    if user is None:
        raise UnauthorizedException(detail="User not found")
    if not user.is_active:
        raise ForbiddenException(detail="Inactive user")
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user

def require_role(allowed_roles: list[UserRole]):
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenException(detail="Operation not permitted")
        return current_user
    return role_checker
