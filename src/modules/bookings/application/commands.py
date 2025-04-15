from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Optional
from uuid import UUID, uuid4

from src.core.events import EventBus
from src.modules.bookings.domain.entities import Booking
from src.modules.bookings.domain.events import BookingCancelled, BookingCreated
from src.modules.bookings.domain.repositories import BookingRepository
from src.modules.bookings.domain.services import BookingValidator
from src.modules.spots.domain.repositories import SpotRepository
from src.modules.users.domain.entities import User


@dataclass
class CreateBookingCommand:
    booking_repo: BookingRepository
    spot_repo: SpotRepository
    event_bus: EventBus
    user_id: UUID
    spot_id: UUID
    time_from: datetime
    time_until: datetime

    async def __call__(self) -> Booking:
        await BookingValidator.validate_booking_time(self.time_from, self.time_until)

        _ = await self.spot_repo.get_by_id(self.spot_id)

        await BookingValidator.check_for_overlapping_bookings(
            self.spot_id,
            self.time_from,
            self.time_until,
            self.booking_repo,
        )

        booking = Booking(
            id=uuid4(),
            user_id=self.user_id,
            spot_id=self.spot_id,
            time_from=self.time_from,
            time_until=self.time_until,
            status='active',
        )

        await self.booking_repo.create(booking)

        await self.event_bus.publish(
            BookingCreated(
                booking_id=booking.id,
                user_id=self.user_id,
                spot_id=self.spot_id,
                time_from=self.time_from,
                time_until=self.time_until,
                timestamp=datetime.now(UTC),
            ),
        )

        return booking


@dataclass
class CancelBookingCommand:
    booking_repo: BookingRepository
    event_bus: EventBus
    booking_id: UUID
    user_id: UUID
    user: Optional[User] = None

    async def __call__(self) -> Booking:
        booking = await self.booking_repo.get_by_id(self.booking_id)

        if not (self.user and self.user.is_business) and booking.user_id != self.user_id:
            msg = 'User is not authorized to cancel this booking'
            raise PermissionError(msg)

        booking.status = 'cancelled'

        updated_booking = await self.booking_repo.update(booking)

        await self.event_bus.publish(
            BookingCancelled(
                booking_id=booking.id,
                user_id=booking.user_id,
                spot_id=booking.spot_id,
                time_from=booking.time_from,
                time_until=booking.time_until,
                timestamp=datetime.now(UTC),
            ),
        )

        return updated_booking
