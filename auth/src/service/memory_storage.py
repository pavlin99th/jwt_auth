from typing import Any
from uuid import UUID, uuid4

from werkzeug.security import generate_password_hash

from schemas.entity import User
from service.base import BaseStorage


class MemoryStorage(BaseStorage):
    """Define memory storage for users."""

    def __init__(self) -> None:
        self.db: dict[UUID, User] = {}
        self._create_dummy_users()

    def _create_dummy_users(self) -> None:
        """Add a couple of users for testing."""

        user1 = User(
            id=uuid4(),
            login="login1",
            password=generate_password_hash("password1"),
            roles={"role1"},
        )
        user2 = User(
            id=uuid4(),
            login="login2",
            password=generate_password_hash("password2"),
            roles={"role2"},
        )
        self.db[user1.id] = user1
        self.db[user2.id] = user2

    async def get(self, id: UUID) -> User | None:
        """Return user by ID."""
        return self.db.get(id)

    async def get_unique_by_attr(self, attr: str, value: Any) -> User | None:
        """Retrieve single user by value of given attribute."""
        for user in self.db.values():
            if getattr(user, attr) == value:
                return user
        return None


storage = MemoryStorage()
