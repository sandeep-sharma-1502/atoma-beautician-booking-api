import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.beautician import BeauticianProfile
from app.schemas.beautician import BeauticianUpdate
from app.core.exceptions import NotFoundException, BadRequestException

from app.core.utils import haversine_distance_km

async def get_beautician_profile(db: AsyncSession, user_id: int) -> BeauticianProfile:
    result = await db.execute(select(BeauticianProfile).where(BeauticianProfile.user_id == user_id))
    profile = result.scalars().first()
    if not profile:
        raise NotFoundException(detail="Beautician profile not found. Please ensure you are registered as a beautician.")
    return profile


async def update_profile(db: AsyncSession, user_id: int, profile_in: BeauticianUpdate) -> BeauticianProfile:
    profile = await get_beautician_profile(db, user_id)

    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    return profile


async def find_available_beauticians(
    db: AsyncSession,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
) -> List[BeauticianProfile]:
    result = await db.execute(select(BeauticianProfile).where(BeauticianProfile.is_available == True))
    profiles = result.scalars().all()

    # Sort by real-world distance when caller provides coordinates.
    # In production with PostgreSQL + PostGIS this would be a single DB-side query.
    if lat is not None and lon is not None:
        profiles = sorted(
            profiles,
            key=lambda p: haversine_distance_km(lat, lon, p.latitude, p.longitude),
        )

    return list(profiles)
