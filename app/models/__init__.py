from app.db.base import Base
from app.models.user import User, UserRole
from app.models.beautician import BeauticianProfile
from app.models.booking import Booking, BookingStatus

# This makes it easy to import all models via app.models.Base metadata for tools like Alembic
