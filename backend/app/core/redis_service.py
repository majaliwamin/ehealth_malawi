import json
import logging
from typing import Optional, Any
from .config import settings

logger = logging.getLogger(__name__)

_redis = None


async def get_redis():
    global _redis
    if not settings.REDIS_URL:
        return None
    if _redis is None:
        try:
            import redis.asyncio as aioredis
            _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            await _redis.ping()
            logger.info("Redis connected: %s", settings.REDIS_URL)
        except Exception as e:
            logger.warning("Redis unavailable (%s) — running without cache", e)
            _redis = None
    return _redis


async def close_redis():
    global _redis
    if _redis:
        await _redis.close()
        _redis = None


async def cache_get(key: str) -> Optional[str]:
    r = await get_redis()
    if not r:
        return None
    try:
        return await r.get(key)
    except Exception:
        return None


async def cache_set(key: str, value: str, ttl: int = 300):
    r = await get_redis()
    if not r:
        return
    try:
        await r.setex(key, ttl, value)
    except Exception:
        pass


async def cache_delete(key: str):
    r = await get_redis()
    if not r:
        return
    try:
        await r.delete(key)
    except Exception:
        pass


async def cache_delete_pattern(pattern: str):
    r = await get_redis()
    if not r:
        return
    try:
        cursor = 0
        while True:
            cursor, keys = await r.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                await r.delete(*keys)
            if cursor == 0:
                break
    except Exception:
        pass


async def publish(channel: str, data: dict):
    r = await get_redis()
    if not r:
        return
    try:
        await r.publish(channel, json.dumps(data))
    except Exception:
        pass
