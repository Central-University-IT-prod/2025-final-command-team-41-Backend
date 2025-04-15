from dataclasses import dataclass
from uuid import UUID, uuid4

from src.modules.spots.domain.entities import Spot
from src.modules.spots.domain.repositories import SpotRepository


@dataclass
class CreateSpotsCommand:
    repo: SpotRepository
    coworking_id: UUID
    spots_data: list[dict]

    async def __call__(self) -> list[Spot]:
        spots = []
        for spot_data in self.spots_data:
            spot = Spot(
                id=uuid4(),
                coworking_id=self.coworking_id,
                name=spot_data['name'],
                description=spot_data['description'],
                position=spot_data['position'],
                status='active',
            )
            spots.append(spot)
            await self.repo.create(spot)
        return spots
