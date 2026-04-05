from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timedelta
from app.models.booking import Booking, BookingStatus
from app.models.beautician import BeauticianProfile
from app.schemas.booking import BookingCreate, BookingUpdate
from app.core.exceptions import BadRequestException, NotFoundException
from app.core.redis import RedisLock
from app.core.utils import haversine_distance_km
import logging

logger = logging.getLogger("atoma.booking")

async def create_booking(db: AsyncSession, customer_id: int, booking_in: BookingCreate) -> Booking:
    """
    Create a booking with a distributed lock to prevent double-booking.
    Uses Redis lock (SETNX) when available, falls back to asyncio.Lock for single-node.
    The critical section atomically claims the NEAREST available beautician.
    """
    async with RedisLock():
        # Re-read inside lock to get fresh state of all available beauticians
        query = select(BeauticianProfile).where(BeauticianProfile.is_available == True)
        result = await db.execute(query)
        beauticians = result.scalars().all()

        if not beauticians:
            raise BadRequestException(detail="No beauticians are currently available")

        # Sort by distance if customer location is provided
        if booking_in.latitude is not None and booking_in.longitude is not None:
            beauticians = sorted(
                beauticians,
                key=lambda b: haversine_distance_km(
                    booking_in.latitude, booking_in.longitude, b.latitude, b.longitude
                )
            )
            logger.info(f"Found {len(beauticians)} available beauticians. Sorting by distance.")
        else:
            logger.warning("Booking request missing location. Assigning first available.")

        locked_beautician_id = None
        for b in beauticians:
            # Atomic UPDATE: only succeeds if is_available is still True
            stmt = (
                update(BeauticianProfile)
                .where(BeauticianProfile.id == b.id, BeauticianProfile.is_available == True)
                .values(is_available=False)
            )
            res = await db.execute(stmt)
            if res.rowcount > 0:
                locked_beautician_id = b.id
                dist = haversine_distance_km(booking_in.latitude, booking_in.longitude, b.latitude, b.longitude) if (booking_in.latitude is not None) else "N/A"
                logger.info(f"Successfully claimed beautician ID={b.id} at distance={dist}km")
                break

        if not locked_beautician_id:
            raise BadRequestException(detail="The closest beauticians were just booked. Please try again.")

        booking = Booking(
            customer_id=customer_id,
            beautician_id=locked_beautician_id,
            scheduled_time=booking_in.scheduled_time.replace(tzinfo=None),
            services_requested=booking_in.services_requested,
            notes=booking_in.notes,
            status=BookingStatus.REQUESTED
        )
        db.add(booking)
        await db.commit()
        await db.refresh(booking)
        return booking


async def get_booking(db: AsyncSession, booking_id: int) -> Booking:
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalars().first()
    if not booking:
        raise NotFoundException(detail="Booking not found")
    return booking

async def update_booking_status(db: AsyncSession, booking_id: int, beautician_id: int, status_in: BookingUpdate) -> Booking:
    booking = await get_booking(db, booking_id)
    
    if booking.beautician_id != beautician_id:
        raise BadRequestException(detail="Not authorized to update this booking")
        
    booking.status = status_in.status
    
    # If completed or cancelled, free the beautician
    if status_in.status in [BookingStatus.COMPLETED, BookingStatus.CANCELLED]:
        # Lock and release
        profile_query = select(BeauticianProfile).where(BeauticianProfile.id == beautician_id).with_for_update()
        prof_res = await db.execute(profile_query)
        profile = prof_res.scalars().first()
        if profile:
            profile.is_available = True

    await db.commit()
    await db.refresh(booking)
    return booking

async def list_all_bookings(db: AsyncSession):
    result = await db.execute(select(Booking))
    return result.scalars().all()
