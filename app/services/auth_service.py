from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User, UserRole
from app.models.beautician import BeauticianProfile
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import BadRequestException

async def get_user_by_email(db: AsyncSession, email: str) -> User:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    existing_user = await get_user_by_email(db, user_in.email)
    if existing_user:
        raise BadRequestException(detail="An account with this email already exists")

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Automatically create an empty beautician profile on BEAUTICIAN signup
    if user.role == UserRole.BEAUTICIAN:
        profile = BeauticianProfile(user_id=user.id)
        db.add(profile)
        await db.commit()

    return user

async def authenticate(db: AsyncSession, email: str, password: str) -> User:
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
