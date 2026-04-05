from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.models.user import User, UserRole
from app.models.booking import Booking, BookingStatus
from app.schemas.booking import BookingResponse
from app.services import booking_service

router = APIRouter()

@router.get("/bookings", response_model=List[BookingResponse], summary="List All Bookings (Admin)")
async def list_all_system_bookings(
    status: Optional[BookingStatus] = Query(None, description="Filter bookings by status"),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.require_role([UserRole.ADMIN])),
):
    """
    **Admin-only.** Returns all bookings in the system.
    Optionally filter by `status`: REQUESTED | ACCEPTED | IN_PROGRESS | COMPLETED | CANCELLED
    """
    query = select(Booking)
    if status:
        query = query.where(Booking.status == status)
    result = await db.execute(query)
    return result.scalars().all()
