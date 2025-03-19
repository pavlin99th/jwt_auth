from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT  # type: ignore
from fastapi import Depends
from redis.asyncio import Redis
from werkzeug.security import check_password_hash

from db.jwt import get_auth
from db.redis import get_redis
from schemas.entity import JWTTokens, User
from service.base import BaseCache, BaseStorage
from service.memory_storage import storage
from service.redis_cache import RedisCache


class UserService:
    """Define user management service."""

    def __init__(
        self,
        storage: BaseStorage,
        cache: BaseCache,
        authorize: AuthJWT,
    ) -> None:
        self.storage = storage
        self.cache = cache
        self.authorize = authorize

    async def _generate_tokens(self, user: User) -> JWTTokens:
        """Generate access and refresh tokens for user."""
        refresh_token = await self.authorize.create_refresh_token(subject=str(user.id))
        rt = await self.authorize.get_raw_jwt(refresh_token)
        roles = list(user.roles)
        access_token = await self.authorize.create_access_token(
            subject=str(user.id), user_claims={"rjti": rt["jti"], "roles": roles}
        )
        await self.cache.add_refresh(user.id, rt)
        return JWTTokens(access_token=access_token, refresh_token=refresh_token)

    async def validate_access(self) -> None:
        """Validate access token."""
        await self.authorize.jwt_required()

    async def validate_refresh(self) -> None:
        """Validate refresh token."""
        await self.authorize.jwt_refresh_token_required()

    async def login_user(self, login: str, password: str) -> JWTTokens | None:
        """Login user and generate tokens."""
        user = await self.storage.get_unique_by_attr("login", login)
        if user is None:
            return None
        if not check_password_hash(user.password, password):
            return None
        return await self._generate_tokens(user)

    async def refresh_user(self) -> JWTTokens:
        """Refresh user's tokens."""
        await self.validate_refresh()

        user_id = UUID(await self.authorize.get_jwt_subject())
        user = await self.storage.get(user_id)
        assert user is not None
        return await self._generate_tokens(user)

    async def logout_user(self) -> None:
        """Logout user and invalidate tokens."""
        await self.validate_access()

        user_id = UUID(await self.authorize.get_jwt_subject())
        at = await self.authorize.get_raw_jwt()
        await self.cache.revoke_access(user_id, at)
        rt = {"jti": at["rjti"]}
        await self.cache.remove_refresh(user_id, rt)

    async def logout_others(self) -> JWTTokens:
        """Logout user's other sessions via not_before mechanism."""
        await self.validate_access()

        user_id = UUID(await self.authorize.get_jwt_subject())
        user = await self.storage.get(user_id)
        assert user is not None
        tokens = await self._generate_tokens(user)
        rt = await self.authorize.get_raw_jwt(tokens.refresh_token)
        await self.cache.set_nbf(user.id, rt)
        return tokens


def get_user_service(
    redis: Redis = Depends(get_redis),
    authorize: AuthJWT = Depends(get_auth),
) -> UserService:
    """Provide user service with Memory storage and Redis token cache."""
    return UserService(
        storage=storage,
        cache=RedisCache(redis),
        authorize=authorize,
    )
