from uuid import UUID

import fastapi

from src.core.database import TransactionManager
from src.core.events import EventBus
from src.modules.auth.domain.services import PasswordHasher
from src.modules.base.domain.value_objects import Pagination
from src.modules.storage.application.services import StorageService
from src.modules.users.application.commands import (
    CreateUserCommand,
    UpdateUserCommand,
    UpdateUserEmailCommand,
)
from src.modules.users.application.queries import GetUserByIdQuery, ListUsersQuery
from src.modules.users.domain.entities import User
from src.modules.users.domain.repositories import UserRepository


class UserService:
    def __init__(
        self,
        repo: UserRepository,
        password_hasher: PasswordHasher,
        event_bus: EventBus,
        transaction_manager: TransactionManager,
        storage_service: StorageService,
    ) -> None:
        self.repo = repo
        self.password_hasher = password_hasher
        self.event_bus = event_bus
        self.transaction_manager = transaction_manager
        self.storage_service = storage_service

    async def create_user(
        self,
        email: str,
        full_name: str,
        password: str,
        is_business: bool,  # noqa
        avatar_url: str | None,
    ) -> User:  # noqa
        async with self.transaction_manager:
            command = CreateUserCommand(
                repo=self.repo,
                email=email,
                full_name=full_name,
                password=password,
                is_business=is_business,
                avatar_url=avatar_url,
                password_hasher=self.password_hasher,
                event_bus=self.event_bus,
            )
            return await command()

    async def update_user_email(self, user_id: UUID, new_email: str) -> User:
        async with self.transaction_manager:
            command = UpdateUserEmailCommand(
                repo=self.repo,
                user_id=user_id,
                new_email=new_email,
                event_bus=self.event_bus,
            )
            return await command()

    async def get_user(self, user_id: UUID) -> User:
        query = GetUserByIdQuery(repo=self.repo)
        return await query(user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.repo.get_by_email(email)

    async def list_users(self, pagination: Pagination) -> list[User]:
        query = ListUsersQuery(repo=self.repo)
        return await query(pagination)

    async def ban_user(self, user_id: UUID) -> None:
        user = await self.repo.get_by_id(user_id)
        user.is_banned = True
        await self.repo.update(user)

    async def unban_user(self, user_id: UUID) -> None:
        user = await self.repo.get_by_id(user_id)
        user.is_banned = False
        await self.repo.update(user)

    async def update_user(
        self,
        user_id: UUID,
        current_user_id: UUID,
        email: str | None = None,
        full_name: str | None = None,
        avatar_url: str | None = None,
    ) -> User:
        await self._check_update_permission(current_user_id, user_id)

        async with self.transaction_manager:
            command = UpdateUserCommand(
                repo=self.repo,
                user_id=user_id,
                email=email,
                full_name=full_name,
                avatar_url=avatar_url,
                event_bus=self.event_bus,
            )
            return await command()

    async def _check_update_permission(self, current_user_id: UUID, target_user_id: UUID) -> None:
        """Check if user has permission to update target user's data."""
        if current_user_id == target_user_id:
            return

        current_user = await self.get_user(current_user_id)
        if not current_user.is_business:
            raise fastapi.exceptions.HTTPException(
                status_code=fastapi.status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this user's data",
            )
