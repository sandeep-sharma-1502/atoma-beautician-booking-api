from pydantic import BaseModel, Field
from app.models.booking import BookingStatus
from datetime import datetime
from typing import Optional

class BookingCreate(BaseModel):
    scheduled_time: datetime = Field(..., description="Desired appointment time (ISO 8601 format)")
    services_requested: str = Field(..., description="Comma-separated list of services, e.g. 'hair, nails'")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Customer's GPS latitude for home service")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Customer's GPS longitude for home service")
    notes: Optional[str] = Field(None, max_length=500, description="Optional customer notes or address details")

class BookingUpdate(BaseModel):
    status: BookingStatus = Field(..., description="New status for the booking")

class BookingResponse(BaseModel):
    id: int
    customer_id: int
    beautician_id: int
    status: BookingStatus
    scheduled_time: datetime
    services_requested: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
