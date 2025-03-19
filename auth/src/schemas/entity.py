from uuid import UUID

from pydantic import BaseModel


class UserLogin(BaseModel):
    """Define login input schema."""

    login: str
    password: str


class User(UserLogin):
    """Define user model."""

    id: UUID
    roles: set[str]


class JWTTokens(BaseModel):
    """Define tokens output schema."""

    access_token: str
    refresh_token: str


class Detail(BaseModel):
    """Define error detail output schema."""

    detail: str
