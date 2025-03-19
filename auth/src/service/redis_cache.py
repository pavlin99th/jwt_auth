from uuid import UUID

from redis.asyncio import Redis

from service.base import BaseCache, Token


class RedisCache(BaseCache):
    """Define Redis cache for tokens."""

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def add_refresh(self, user_id: UUID, rt: Token) -> None:
        """Add refresh token to user's set."""
        rt_set = f"refresh:{user_id}"
        await self.redis.sadd(rt_set, rt["jti"])  # type: ignore
        await self.redis.expireat(rt_set, rt["exp"])

    async def check_refresh(self, user_id: UUID, rt: Token) -> bool:
        """Check for refresh token in user's set."""
        jti = rt["jti"]
        is_valid = await self.redis.sismember(f"refresh:{user_id}", jti)  # type: ignore
        return bool(is_valid)

    async def remove_refresh(self, user_id: UUID, rt: Token) -> None:
        """Remove refresh token from user's set."""
        jti = rt["jti"]
        await self.redis.srem(f"refresh:{user_id}", jti)  # type: ignore

    async def revoke_access(self, user_id: UUID, at: Token) -> None:
        """Add access token to revocation set."""
        at_set = f"revoked:{user_id}"
        await self.redis.sadd(at_set, at["jti"])  # type: ignore
        await self.redis.expireat(at_set, at["exp"])

    async def check_access(self, user_id: UUID, at: Token) -> bool:
        """Check access token for revocation."""
        jti = at["jti"]
        is_revoked = await self.redis.sismember(f"revoked:{user_id}", jti)  # type: ignore
        return not is_revoked

    async def set_nbf(self, user_id: UUID, rt: Token) -> None:
        """Set not_before timestamp based on given refresh token."""
        nbf_key = f"not_before:{user_id}"
        await self.redis.set(nbf_key, rt["iat"])
        await self.redis.expireat(nbf_key, rt["exp"])

    async def check_nbf(self, user_id: UUID, at_or_rt: Token) -> bool:
        """Check token issue time against not_before key."""
        not_before = await self.redis.get(f"not_before:{user_id}")
        if not_before is not None and at_or_rt["iat"] < int(not_before):
            return False
        return True
