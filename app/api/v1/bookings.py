from typing import List
from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.models.user import User, UserRole
from app.schemas.booking import BookingCreate, BookingResponse, BookingUpdate
from app.services import booking_service, beautician_service
import asyncio
import logging

logger = logging.getLogger("atoma")

router = APIRouter()

async def process_booking_queue(booking_id: int):
    """Simulate a background queue task, e.g. sending emails or notifications."""
    await asyncio.sleep(2)  # simulate processing delay
    logger.info(f"Queue Task: Processed booking {booking_id} successfully.")

@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_in: BookingCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.require_role([UserRole.CUSTOMER])),
):
    """Create a new booking and automatically assign an available beautician."""
    booking = await booking_service.create_booking(db, customer_id=current_user.id, booking_in=booking_in)
    
    # Add to background queue
    background_tasks.add_task(process_booking_queue, booking.id)
    
    return booking

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get details of a specific booking."""
    booking = await booking_service.get_booking(db, booking_id=booking_id)
    return booking

@router.put("/{booking_id}/status", response_model=BookingResponse)
async def update_booking_status(
    booking_id: int,
    status_in: BookingUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.require_role([UserRole.BEAUTICIAN]))
):
    """Beautician updates the status of the booking."""
    profile = await beautician_service.get_beautician_profile(db, current_user.id)
    booking = await booking_service.update_booking_status(
        db, booking_id=booking_id, beautician_id=profile.id, status_in=status_in
    )
    return booking
