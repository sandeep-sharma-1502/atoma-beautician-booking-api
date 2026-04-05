from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin

class BeauticianProfile(Base, TimestampMixin):
    __tablename__ = "beautician_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    bio = Column(Text, nullable=True)
    # Comma-separated for SQLite portability; use ARRAY/JSONB on PostgreSQL
    services_offered = Column(String, default="")
    is_available = Column(Boolean, default=True, index=True)

    # GPS coordinates for nearest-beautician lookup
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    user = relationship("User", back_populates="beautician_profile")
    bookings = relationship("Booking", back_populates="beautician", foreign_keys="[Booking.beautician_id]")
