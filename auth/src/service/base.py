from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from schemas.entity import User


class BaseStorage(ABC):
    """Base class for users storage."""

    @abstractmethod
    async def get(self, id: UUID) -> User | None:
        """Get user from storage by ID."""
        pass

    @abstractmethod
    async def get_unique_by_attr(self, attr: str, value: Any) -> User | None:
        """Retrieve a unique user by a specific attribute."""
        pass


Token = dict[str, Any]


class BaseCache(ABC):
    """Base class for token cache."""

    @abstractmethod
    async def add_refresh(self, user_id: UUID, rt: Token) -> None:
        """Add refresh token to cache."""
        pass

    @abstractmethod
    async def check_refresh(self, user_id: UUID, rt: Token) -> bool:
        """Check presence of refresh token in cache."""
        pass

    @abstractmethod
    async def remove_refresh(self, user_id: UUID, rt: Token) -> None:
        """Remove refresh token from cache."""
        pass

    @abstractmethod
    async def revoke_access(self, user_id: UUID, rt: Token) -> None:
        """Invalidate access token."""
        pass

    @abstractmethod
    async def check_access(self, user_id: UUID, rt: Token) -> bool:
        """Check access token for revocation."""
        pass

    @abstractmethod
    async def set_nbf(self, user_id: UUID, rt: Token) -> None:
        """Set not_before timestamp based on supplied token."""
        pass

    @abstractmethod
    async def check_nbf(self, user_id: UUID, at_or_rt: Token) -> bool:
        """Check not_before timestamp against given token."""
        pass
