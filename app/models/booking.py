import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin

class BookingStatus(str, enum.Enum):
    REQUESTED = "REQUESTED"
    ACCEPTED = "ACCEPTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class Booking(Base, TimestampMixin):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    beautician_id = Column(Integer, ForeignKey("beautician_profiles.id"), nullable=False)

    status = Column(Enum(BookingStatus), default=BookingStatus.REQUESTED, nullable=False, index=True)
    scheduled_time = Column(DateTime, nullable=False)
    services_requested = Column(String, nullable=True)  # mirrors services_offered format
    notes = Column(Text, nullable=True)

    customer = relationship("User", back_populates="customer_bookings", foreign_keys=[customer_id])
    beautician = relationship("BeauticianProfile", back_populates="bookings", foreign_keys=[beautician_id])
