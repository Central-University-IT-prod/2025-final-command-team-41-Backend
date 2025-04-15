from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.core.events import EventBus
from src.modules.auth.domain.services import PasswordHasher
from src.modules.users.domain.entities import User
from src.modules.users.domain.events import (
    UserCreated,
    UserEmailChanged,
)
from src.modules.users.domain.repositories import UserRepository
from src.modules.users.domain.services import UserValidator


@dataclass
class CreateUserCommand:
    repo: UserRepository
    email: str
    full_name: str
    password: str
    is_business: bool
    avatar_url: str | None
    password_hasher: PasswordHasher
    event_bus: EventBus

    async def __call__(self) -> User:
        await UserValidator.check_email_unique(self.email, self.repo)
        hashed_password = await self.password_hasher.hash_password(self.password)
        user = User(
            id=uuid4(),
            email=self.email,
            full_name=self.full_name,
            avatar_url=self.avatar_url,
            hashed_password=hashed_password,
            is_business=self.is_business,
        )
        await self.repo.create(user)
        await self.event_bus.publish(
            UserCreated(
                user_id=user.id,
                email=self.email,
                full_name=self.full_name,
                timestamp=datetime.now(UTC),
            ),
        )
        return user


@dataclass
class UpdateUserEmailCommand:
    repo: UserRepository
    user_id: UUID
    new_email: str
    event_bus: EventBus

    async def __call__(self) -> User:
        user = await self.repo.get_by_id(self.user_id)

        old_email = user.email
        if old_email != self.new_email:
            await UserValidator.check_email_unique(self.new_email, self.repo)
            user.change_email(self.new_email)
            await self.repo.update(user)

            await self.event_bus.publish(
                UserEmailChanged(
                    user_id=self.user_id,
                    old_email=old_email,
                    new_email=self.new_email,
                    timestamp=datetime.now(UTC),
                ),
            )

        return user


@dataclass
class UpdateUserCommand:
    repo: UserRepository
    user_id: UUID
    email: str | None = None
    full_name: str | None = None
    avatar_url: str | None = None
    event_bus: EventBus | None = None

    async def __call__(self) -> User:
        user = await self.repo.get_by_id(self.user_id)

        if self.email is not None and user.email != self.email:
            await UserValidator.check_email_unique(self.email, self.repo)
            old_email = user.email
            user.change_email(self.email)

            if self.event_bus:
                await self.event_bus.publish(
                    UserEmailChanged(
                        user_id=self.user_id,
                        old_email=old_email,
                        new_email=self.email,
                        timestamp=datetime.now(UTC),
                    ),
                )

        if self.full_name is not None:
            user.full_name = self.full_name

        if self.avatar_url is not None:
            user.avatar_url = self.avatar_url

        await self.repo.update(user)
        return user
