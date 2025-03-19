import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from async_fastapi_jwt_auth.exceptions import AuthJWTException  # type: ignore
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.v1 import auth
from core.config import settings
from db import redis

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage startup / shutdown operations."""
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    yield
    await redis.redis.aclose()


app = FastAPI(
    title="Auth API",
    description="Аутентификация и авторизация пользователей.",
    version="1.0.0",
    docs_url="/api/openapi/",
    openapi_url="/api/openapi/api.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)
app.include_router(auth.router, prefix="/api/v1/auth")


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException) -> ORJSONResponse:
    return ORJSONResponse(status_code=exc.status_code, content={"detail": exc.message})
