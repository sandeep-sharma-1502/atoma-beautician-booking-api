from sqlalchemy import Column, Integer, String, Boolean, Enum
import enum
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"
    BEAUTICIAN = "BEAUTICIAN"

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    is_active = Column(Boolean, default=True)

    beautician_profile = relationship("BeauticianProfile", back_populates="user", uselist=False)
    customer_bookings = relationship("Booking", back_populates="customer", foreign_keys="[Booking.customer_id]")
