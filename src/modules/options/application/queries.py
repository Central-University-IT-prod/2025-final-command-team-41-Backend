from uuid import UUID

from src.modules.base.domain.value_objects import Pagination
from src.modules.options.domain.entities import Option
from src.modules.options.domain.repositories import OptionRepository


class ListOptionsQuery:
    def __init__(self, repo: OptionRepository) -> None:
        self.repo = repo

    async def __call__(self, pagination: Pagination) -> list[Option]:
        return await self.repo.get_all_paginated(pagination)


class GetOptionsByCoworkingIdQuery:
    def __init__(self, repo: OptionRepository) -> None:
        self.repo = repo

    async def __call__(self, coworking_id: UUID) -> list[Option]:
        return await self.repo.get_by_coworking_id(coworking_id)
