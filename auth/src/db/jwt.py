from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT  # type: ignore
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer  # type: ignore

from core.config import Settings, settings
from db.redis import get_redis
from service.redis_cache import RedisCache

get_auth = AuthJWTBearer()


@AuthJWT.load_config  # type: ignore
def get_config() -> Settings:
    """Provide config to jwt module."""
    return settings


@AuthJWT.token_in_denylist_loader  # type: ignore
async def validate_jwt(decrypted_token) -> bool:
    """Define token deny list validator callback for jwt module."""
    cache = RedisCache(await get_redis())
    user_id = UUID(decrypted_token["sub"])
    if not await cache.check_nbf(user_id, decrypted_token):
        return True
    token_type = decrypted_token["type"]
    if token_type == "access":
        is_valid = await cache.check_access(user_id, decrypted_token)
    elif token_type == "refresh":
        is_valid = await cache.check_refresh(user_id, decrypted_token)
        if is_valid:
            await cache.remove_refresh(user_id, decrypted_token)
    return not is_valid
