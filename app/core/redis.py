import json
from typing import Optional
import redis.asyncio as redis
from app.core.config import settings
import asyncio
import logging

logger = logging.getLogger("atoma")

# Initialize global Redis client instance
redis_client: Optional[redis.Redis] = None

# Fallback in-process lock used when Redis is not available
_booking_lock = asyncio.Lock()

async def setup_redis():
    global redis_client
    if settings.REDIS_URL:
        try:
            redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            await redis_client.ping()
            logger.info("Connected to Redis cache.")
        except Exception as e:
            logger.error(f"Failed to connect to Redis, falling back to no-cache: {e}")
            redis_client = None

def get_redis_client() -> Optional[redis.Redis]:
    return redis_client

class RedisLock:
    """
    Redis-based distributed lock with asyncio.Lock fallback.
    If Redis is available, acquires a SETNX-based lock.
    Otherwise falls back to a simple in-process asyncio.Lock.
    """
    LOCK_KEY = "lock:booking_assignment"
    LOCK_TTL = 10  # seconds

    def __init__(self):
        self._redis = get_redis_client()

    async def __aenter__(self):
        if self._redis:
            # Spin-wait up to 5s for the Redis lock
            for _ in range(50):
                acquired = await self._redis.set(
                    self.LOCK_KEY, "1", nx=True, ex=self.LOCK_TTL
                )
                if acquired:
                    return self
                await asyncio.sleep(0.1)
            raise RuntimeError("Could not acquire booking lock (timeout)")
        else:
            await _booking_lock.acquire()
            return self

    async def __aexit__(self, *args):
        if self._redis:
            await self._redis.delete(self.LOCK_KEY)
        else:
            _booking_lock.release()
