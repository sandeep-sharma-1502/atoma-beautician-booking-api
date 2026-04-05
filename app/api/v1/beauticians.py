from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.models.user import User, UserRole
from app.schemas.beautician import BeauticianResponse, BeauticianUpdate
from app.services import beautician_service
from app.core.redis import get_redis_client
import json

router = APIRouter()

@router.get("/", response_model=List[BeauticianResponse])
async def list_available_beauticians(
    lat: Optional[float] = Query(None, description="Latitude for nearest search"),
    lon: Optional[float] = Query(None, description="Longitude for nearest search"),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """List all available beauticians, optionally sorted by distance."""
    cache_key = f"beauticians:{lat}:{lon}"
    redis = get_redis_client()
    
    if redis:
        cached_data = await redis.get(cache_key)
        if cached_data:
            return json.loads(cached_data)

    profiles = await beautician_service.find_available_beauticians(db, lat=lat, lon=lon)
    response_data = [BeauticianResponse.model_validate(p).model_dump(mode="json") for p in profiles]
    
    if redis:
        await redis.setex(cache_key, 60, json.dumps(response_data)) # Cache for 60 seconds
        
    return response_data

@router.put("/me", response_model=BeauticianResponse)
async def update_my_beautician_profile(
    profile_in: BeauticianUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.require_role([UserRole.BEAUTICIAN])),
):
    """Update logged-in beautician's profile and availability."""
    profile = await beautician_service.update_profile(db, user_id=current_user.id, profile_in=profile_in)
    return profile
