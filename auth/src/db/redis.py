from redis.asyncio import Redis

redis: Redis | None = None


async def get_redis() -> Redis:
    """Provide Redis client."""
    if redis is None:
        raise RuntimeError("redis instance is not initialized")
    return redis
