from uuid import UUID

from src.modules.base.domain.repositories import BaseRepository
from src.modules.options.domain.entities import Option


class OptionRepository(BaseRepository[Option]):
    async def get_by_coworking_id(self, coworking_id: UUID) -> list[Option]: ...
