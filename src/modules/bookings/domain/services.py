from datetime import datetime
from uuid import UUID

from src.modules.bookings.domain.exceptions import (
    BookingOverlapError,
    InvalidBookingTimeError,
)
from src.modules.bookings.domain.repositories import BookingRepository


class BookingValidator:
    @staticmethod
    async def validate_booking_time(
        time_from: datetime,
        time_until: datetime,
    ) -> None:
        if time_from >= time_until:
            msg = 'Start time must be before end time'
            raise InvalidBookingTimeError(msg)

    @staticmethod
    async def check_for_overlapping_bookings(
        spot_id: UUID,
        time_from: datetime,
        time_until: datetime,
        repo: BookingRepository,
    ) -> None:
        existing_bookings = await repo.get_active_bookings_in_time_range(
            spot_id,
            time_from,
            time_until,
        )

        if existing_bookings:
            msg = 'Spot is already booked during this time'
            raise BookingOverlapError(msg)
