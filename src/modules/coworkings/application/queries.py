from uuid import UUID

from src.modules.base.domain.value_objects import Pagination
from src.modules.coworkings.domain.entities import Coworking
from src.modules.coworkings.domain.repositories import CoworkingRepository


class GetCoworkingByIdQuery:
    def __init__(self, repo: CoworkingRepository) -> None:
        self.repo = repo

    async def __call__(self, coworking_id: UUID) -> Coworking:
        return await self.repo.get_by_id(coworking_id)


class ListCoworkingsQuery:
    def __init__(self, repo: CoworkingRepository) -> None:
        self.repo = repo

    async def __call__(self, pagination: Pagination) -> list[Coworking]:
        return await self.repo.get_all_paginated(pagination)
