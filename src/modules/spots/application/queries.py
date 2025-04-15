from uuid import UUID

from src.modules.spots.domain.entities import Spot
from src.modules.spots.domain.repositories import SpotRepository


class GetSpotsByCoworkingIdQuery:
    def __init__(self, repo: SpotRepository) -> None:
        self.repo = repo

    async def __call__(self, coworking_id: UUID) -> list[Spot]:
        return await self.repo.get_by_coworking_id(coworking_id)
