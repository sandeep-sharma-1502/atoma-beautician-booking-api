from fastapi import APIRouter
from app.api.v1 import auth, beauticians, bookings, admin

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(beauticians.router, prefix="/beauticians", tags=["beauticians"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
