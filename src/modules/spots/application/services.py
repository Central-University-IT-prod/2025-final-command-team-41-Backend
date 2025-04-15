from datetime import datetime
from typing import Any, Optional, TypedDict
from uuid import UUID

from src.core.database import TransactionManager
from src.modules.bookings.domain.repositories import BookingRepository
from src.modules.spots.application.commands import CreateSpotsCommand
from src.modules.spots.application.queries import GetSpotsByCoworkingIdQuery
from src.modules.spots.domain.entities import Spot
from src.modules.spots.domain.repositories import SpotRepository


class SpotWithStatusDict(TypedDict):
    id: UUID
    coworking_id: UUID
    name: str
    description: str
    position: int
    status: str


class SpotService:
    def __init__(
        self,
        repo: SpotRepository,
        transaction_manager: TransactionManager,
        booking_repo: Optional[BookingRepository] = None,
    ) -> None:
        self.repo = repo
        self.transaction_manager = transaction_manager
        self.booking_repo = booking_repo

    async def get_spots_by_coworking_id(self, coworking_id: UUID) -> list[Spot]:
        query = GetSpotsByCoworkingIdQuery(repo=self.repo)
        return await query(coworking_id)

    async def create_spots(self, coworking_id: UUID, spots_data: list[dict[str, Any]]) -> list[Spot]:
        async with self.transaction_manager:
            command = CreateSpotsCommand(
                repo=self.repo,
                coworking_id=coworking_id,
                spots_data=spots_data,
            )
            return await command()

    async def get_spots_with_availability(
        self,
        coworking_id: UUID,
        time_from: datetime,
        time_until: datetime,
    ) -> list[tuple[Spot, str]]:
        if not self.booking_repo:
            spots = await self.get_spots_by_coworking_id(coworking_id)
            return [(spot, 'active') for spot in spots]

        spots = await self.get_spots_by_coworking_id(coworking_id)

        if not spots:
            return []

        spot_ids = [spot.id for spot in spots]

        booked_spots = await self.booking_repo.get_active_bookings_for_spots(
            spot_ids,
            time_from,
            time_until,
        )

        booked_spot_ids = {booking.spot_id for booking in booked_spots}

        return [(spot, 'inactive' if spot.id in booked_spot_ids else 'active') for spot in spots]

    async def get_spots_with_status(
        self,
        coworking_id: UUID,
        time_from: Optional[datetime] = None,
        time_until: Optional[datetime] = None,
    ) -> list[SpotWithStatusDict]:
        if time_from and time_until:
            spots_with_status = await self.get_spots_with_availability(
                coworking_id=coworking_id,
                time_from=time_from,
                time_until=time_until,
            )

            return [
                {
                    'id': spot.id,
                    'coworking_id': spot.coworking_id,
                    'name': spot.name,
                    'description': spot.description,
                    'position': spot.position,
                    'status': status,
                }
                for spot, status in spots_with_status
            ]

        spots = await self.get_spots_by_coworking_id(coworking_id)
        return [
            {
                'id': spot.id,
                'coworking_id': spot.coworking_id,
                'name': spot.name,
                'description': spot.description,
                'position': spot.position,
                'status': 'active',
            }
            for spot in spots
        ]
