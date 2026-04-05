from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class BeauticianUpdate(BaseModel):
    bio: Optional[str] = Field(None, max_length=1000, description="Short biography of the beautician")
    services_offered: Optional[str] = Field(None, description="Comma-separated list of services, e.g. 'hair, nails, makeup'")
    is_available: Optional[bool] = Field(None, description="Whether the beautician is open for new bookings")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="GPS latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="GPS longitude")

class BeauticianResponse(BaseModel):
    id: int
    user_id: int
    bio: Optional[str] = None
    services_offered: str
    is_available: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
