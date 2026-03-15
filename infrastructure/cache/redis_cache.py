import json
import redis.asyncio as redis
import logging
from typing import Union, Dict

from domain.interfaces import RedisCacheRepositoryInterface
from stackexchange.settings import settings


logger = logging.getLogger("stackexchange_api")

class RedisCacheRepository(RedisCacheRepositoryInterface):
    """
    Handles caching of responses in Redis.
    """

    def __init__(self, redis_client: redis.Redis, ttl: int = settings.TTL):
        """
        Args:
            redis_client: Async Redis client instance.
            ttl: Default time-to-live in seconds for cached entries.
        """
        self._client = redis_client
        self._ttl = ttl

    async def get(self, key: str) -> Union[None, Dict]:
        """
        Retrieve a cached value by key.

        Args:
            key: Cache key to look up.

        Returns:
            Parsed dictionary if found, None otherwise.
        """
        try:
            value = await self._client.get(key)
            if value:
                logger.info("Cache hit for key: %s", key)
                return json.loads(value)
            logger.info("Cache miss for key: %s", key)
            return None
        except Exception as e:
            logger.error("Error retrieving cache for key %s: %s", key, e)
            return None

    async def set(self, key: str, value: dict, ttl: int = None):
        """
        Store a value in the cache.

        Args:
            key: Cache key to store the value under.
            value: Dictionary to serialize and cache.
            ttl: Time-to-live in seconds. Falls back to the instance default if not provided.
        """
        ttl = ttl or self._ttl
        try:
            await self._client.set(key, json.dumps(value), ex=ttl)
            logger.info("Cache set for key: %s", key)
        except Exception as e:
            logger.error("Error setting cache for key %s: %s", key, e)
