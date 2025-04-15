from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from src.modules.bookings.domain.repositories import BookingRepository
from src.modules.coworkings.domain.repositories import CoworkingRepository
from src.modules.spots.domain.repositories import SpotRepository


class GetUserBookingsQuery:
    def __init__(
        self,
        booking_repo: BookingRepository,
        spot_repo: SpotRepository,
        coworking_repo: CoworkingRepository,
    ) -> None:
        self.booking_repo = booking_repo
        self.spot_repo = spot_repo
        self.coworking_repo = coworking_repo

    async def __call__(self, user_id: UUID) -> list[dict[str, Any]]:
        bookings = await self.booking_repo.get_by_user_id(user_id)

        current_time = datetime.now(UTC)
        for booking in bookings:
            booking.status = booking.get_effective_status(current_time)

        result: list[dict[str, Any]] = []

        for booking in bookings:
            spot = await self.spot_repo.get_by_id(booking.spot_id)

            coworking = await self.coworking_repo.get_by_id(spot.coworking_id)

            booking_data: dict[str, Any] = {
                'id': booking.id,
                'user_id': booking.user_id,
                'time_from': booking.time_from,
                'time_until': booking.time_until,
                'status': booking.status,
                'coworking': {
                    'id': coworking.id,
                    'name': coworking.name,
                    'address': coworking.address,
                    'opens_at': coworking.opens_at,
                    'closes_at': coworking.closes_at,
                    'spot': {
                        'id': spot.id,
                        'name': spot.name,
                        'description': spot.description,
                    },
                },
            }

            result.append(booking_data)

        return result
