import asyncio
import aiohttp
import redis.asyncio as redis
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from api.routes import router
from application.services.calculator import Calculator
from application.services.stackexchange import StackExchangeService
from infrastructure.cache.redis_cache import RedisCacheRepository
from infrastructure.client.stackexchange import StackExchangeClient
from stackexchange.settings import settings


logger = logging.getLogger("stackexchange_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context to initialize resources (HTTP session, Redis, clients, services)
    and handle graceful shutdown.

    Args:
        app: The FastAPI application instance.

    Yields:
        Control back to FastAPI while the application is running.
    """
    logger.info("Starting application...")
    
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT))
    redis_client = redis.from_url(settings.REDIS_URL)
    semaphore = asyncio.Semaphore(settings.MAX_CONCURRENCY)

    # Initialize infrastructure
    app.state.redis_cache = RedisCacheRepository(redis_client, ttl=settings.TTL)
    app.state.stackexchange_client = StackExchangeClient(
        key=settings.STACKEXCHANGE_KEY,
        base_url=settings.STACKEXCHANGE_BASE_URL,
        site=settings.STACKEXCHANGE_SITE,
        session=session,
        semaphore=semaphore,
    )
    app.state.calculator = Calculator()

    # Initialize service layer
    app.state.stack_service = StackExchangeService(
        client=app.state.stackexchange_client,
        cache=app.state.redis_cache,
        calculator=app.state.calculator,
    )

    yield

    # Graceful shutdown
    logger.info("Shutting down application...")
    await session.close()
    await redis_client.close()
