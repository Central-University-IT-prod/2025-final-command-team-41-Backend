from datetime import datetime
from uuid import UUID

from src.modules.base.domain.repositories import BaseRepository
from src.modules.base.domain.value_objects import Pagination
from src.modules.bookings.domain.entities import Booking


class BookingRepository(BaseRepository[Booking]):
    async def get_by_user_id(self, user_id: UUID) -> list[Booking]: ...

    async def get_by_spot_id(self, spot_id: UUID) -> list[Booking]: ...

    async def count_all(self) -> int: ...

    async def get_all_paginated(self, pagination: Pagination) -> list[Booking]: ...

    async def get_active_bookings_in_time_range(
        self,
        spot_id: UUID,
        time_from: datetime,
        time_until: datetime,
    ) -> list[Booking]: ...

    async def get_active_bookings_for_spots(
        self,
        spot_ids: list[UUID],
        time_from: datetime,
        time_until: datetime,
    ) -> list[Booking]: ...
