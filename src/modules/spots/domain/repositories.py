from uuid import UUID

from src.modules.base.domain.repositories import BaseRepository
from src.modules.spots.domain.entities import Spot


class SpotRepository(BaseRepository[Spot]):
    async def get_by_coworking_id(self, coworking_id: UUID) -> list[Spot]: ...
