import json
import redis.asyncio as redis
from typing import Any, Optional
from app.config import settings


class CacheService:
    _client: Optional[redis.Redis] = None

    @classmethod
    async def get_client(cls) -> redis.Redis:
        if cls._client is None:
            cls._client = await redis.from_url(settings.REDIS_URL, decode_responses=True)
        return cls._client

    @classmethod
    async def get(cls, key: str) -> Optional[Any]:
        """Get value from cache, returns None if not found or expired"""
        try:
            client = await cls.get_client()
            value = await client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception:
            return None

    @classmethod
    async def set(cls, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL in seconds"""
        try:
            client = await cls.get_client()
            serialized = json.dumps(value, default=str)
            await client.setex(key, ttl, serialized)
            return True
        except Exception:
            return False

    @classmethod
    async def delete(cls, key: str) -> bool:
        """Delete a key from cache"""
        try:
            client = await cls.get_client()
            await client.delete(key)
            return True
        except Exception:
            return False

    @classmethod
    async def invalidate_pattern(cls, pattern: str) -> int:
        """Delete all keys matching a pattern"""
        try:
            client = await cls.get_client()
            cursor = 0
            count = 0
            while True:
                cursor, keys = await client.scan(cursor, match=pattern)
                if keys:
                    await client.delete(*keys)
                    count += len(keys)
                if cursor == 0:
                    break
            return count
        except Exception:
            return 0

    @classmethod
    async def close(cls):
        """Close Redis connection"""
        if cls._client:
            await cls._client.close()
            cls._client = None


# Singleton instance
cache = CacheService()
