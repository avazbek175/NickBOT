import json
from typing import Optional, Any
from redis.asyncio import Redis as AsyncRedis
from src.config import config

redis: Optional[AsyncRedis] = None


async def init_redis():
    global redis
    redis = AsyncRedis.from_url(config.redis_url, decode_responses=True)
    await redis.ping()


async def close_redis():
    global redis
    if redis:
        await redis.aclose()


async def set_cache(key: str, value: Any, ttl: int = 300):
    if redis:
        await redis.set(key, json.dumps(value), ex=ttl)


async def get_cache(key: str) -> Optional[Any]:
    if redis:
        data = await redis.get(key)
        return json.loads(data) if data else None
    return None


async def delete_cache(key: str):
    if redis:
        await redis.delete(key)


async def cache_keys(pattern: str) -> list:
    if redis:
        return await redis.keys(pattern)
    return []
