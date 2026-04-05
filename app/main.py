from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.logging import setup_logging, LoggingMiddleware
from app.core.exceptions import AppException, app_exception_handler
from app.db.session import engine
from app.db.base import Base
from app.core.redis import setup_redis

# Ensure all models are loaded so SQLAlchemy metadata is complete
from app.models import *

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages startup and shutdown of shared resources."""
    # --- Startup ---
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await setup_redis()
    yield
    # --- Shutdown ---
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description=(
        "**Atoma** – Backend service for a beautician home-services booking platform.\n\n"
        "## Authentication\n"
        "Use `POST /api/v1/auth/register` to create an account, then `POST /api/v1/auth/token` "
        "to obtain a **Bearer** JWT. Paste the token into the **Authorize** button above to unlock "
        "protected endpoints.\n\n"
        "## Roles\n"
        "- `CUSTOMER` – create bookings\n"
        "- `BEAUTICIAN` – manage profile, update booking status\n"
        "- `ADMIN` – view & filter all bookings\n\n"
        "## Concurrency Safety\n"
        "Booking assignment uses a **Redis SETNX distributed lock** (falls back to an "
        "`asyncio.Lock` when Redis is unavailable) to guarantee zero double-bookings under "
        "high concurrent traffic."
    ),
    contact={"name": "Atoma Team"},
    license_info={"name": "Private"},
    lifespan=lifespan,
)

# --- Exception Handlers ---
app.add_exception_handler(AppException, app_exception_handler)

# --- Middlewares ---
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["system"], summary="Health Check")
async def health_check():
    """Returns the operational status of the API server and Redis connection status."""
    from app.core.redis import get_redis_client
    
    redis_status = "unavailable"
    client = get_redis_client()
    if client:
        try:
            await client.ping()
            redis_status = "ok"
        except Exception:
            redis_status = "error"

    return {
        "status": "ok", 
        "version": settings.VERSION, 
        "service": settings.PROJECT_NAME,
        "redis_status": redis_status
    }
