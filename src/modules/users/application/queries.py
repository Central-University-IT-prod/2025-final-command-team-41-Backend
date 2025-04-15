from uuid import UUID

from src.modules.base.domain.value_objects import Pagination
from src.modules.users.domain.entities import User
from src.modules.users.domain.repositories import UserRepository


class GetUserByIdQuery:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    async def __call__(self, user_id: UUID) -> User:
        return await self.repo.get_by_id(user_id)


class ListUsersQuery:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    async def __call__(self, pagination: Pagination) -> list[User]:
        return await self.repo.get_all_paginated(pagination)
