from datetime import UTC, datetime, time, timezone
from typing import Any, Optional
from uuid import UUID

from src.core.database import TransactionManager
from src.core.events import EventBus
from src.core.timezone_utils import DEFAULT_TIMEZONE_OFFSET, to_client_timezone, to_utc
from src.modules.base.domain.value_objects import Pagination
from src.modules.bookings.application.commands import CancelBookingCommand, CreateBookingCommand
from src.modules.bookings.application.queries import GetUserBookingsQuery
from src.modules.bookings.domain.entities import Booking
from src.modules.bookings.domain.exceptions import (
    BookingAccessDeniedError,
    BookingOverlapError,
    SpotHasNoCurrentBookingError,
)
from src.modules.bookings.domain.repositories import BookingRepository
from src.modules.coworkings.domain.repositories import CoworkingRepository
from src.modules.options.domain.exceptions import OptionNotFoundError
from src.modules.options.domain.repositories import OptionRepository
from src.modules.spots.domain.entities import Spot
from src.modules.spots.domain.repositories import SpotRepository
from src.modules.users.domain.repositories import UserRepository

TimeSlot = dict[str, datetime]


class BookingService:
    def __init__(
        self,
        booking_repo: BookingRepository,
        spot_repo: SpotRepository,
        coworking_repo: CoworkingRepository,
        event_bus: EventBus,
        transaction_manager: TransactionManager,
        user_repo: Optional[UserRepository] = None,
        option_repo: Optional[OptionRepository] = None,
    ) -> None:
        self.booking_repo = booking_repo
        self.spot_repo = spot_repo
        self.coworking_repo = coworking_repo
        self.event_bus = event_bus
        self.transaction_manager = transaction_manager
        self.user_repo = user_repo
        self.option_repo = option_repo

    async def create_booking(
        self,
        user_id: UUID,
        spot_id: UUID,
        time_from: datetime,
        time_until: datetime,
    ) -> dict[str, Any]:
        time_from_utc = to_utc(time_from)
        time_until_utc = to_utc(time_until)

        async with self.transaction_manager:
            command = CreateBookingCommand(
                booking_repo=self.booking_repo,
                spot_repo=self.spot_repo,
                event_bus=self.event_bus,
                user_id=user_id,
                spot_id=spot_id,
                time_from=time_from_utc,
                time_until=time_until_utc,
            )
            booking = await command()

            bookings = await self.get_user_bookings(user_id)
            for b in bookings:
                if b['id'] == booking.id:
                    return b

            return {
                'id': booking.id,
                'user_id': booking.user_id,
                'time_from': to_client_timezone(booking.time_from),
                'time_until': to_client_timezone(booking.time_until),
                'status': booking.status,
            }

    async def get_user_bookings(self, user_id: UUID) -> list[dict[str, Any]]:
        query = GetUserBookingsQuery(
            booking_repo=self.booking_repo,
            spot_repo=self.spot_repo,
            coworking_repo=self.coworking_repo,
        )
        bookings = await query(user_id)

        for booking in bookings:
            booking['time_from'] = to_client_timezone(booking['time_from'])
            booking['time_until'] = to_client_timezone(booking['time_until'])

        return bookings

    async def cancel_booking(self, booking_id: UUID, user_id: UUID) -> Booking:
        async with self.transaction_manager:
            user = None
            if self.user_repo:
                user = await self.user_repo.get_by_id(user_id)

            command = CancelBookingCommand(
                booking_repo=self.booking_repo,
                event_bus=self.event_bus,
                booking_id=booking_id,
                user_id=user_id,
                user=user,
            )
            return await command()

    async def get_booking_by_id(self, booking_id: UUID) -> Booking:
        booking = await self.booking_repo.get_by_id(booking_id)
        booking.status = booking.get_effective_status()
        return booking

    async def get_booking_by_id_with_permission_check(
        self,
        booking_id: UUID,
        user_id: UUID,
    ) -> dict[str, Any]:
        booking = await self._check_permission(booking_id, user_id)
        booking.status = booking.get_effective_status()

        if self.user_repo:
            booking_user = await self.user_repo.get_by_id(booking.user_id)
        else:
            booking_user = None

        spot = await self.spot_repo.get_by_id(booking.spot_id)

        return {
            'id': booking.id,
            'user': {
                'id': booking_user.id if booking_user else booking.user_id,
                'avatar_url': booking_user.avatar_url if booking_user else None,
                'full_name': booking_user.full_name if booking_user else '',
                'email': booking_user.email if booking_user else '',
            },
            'spot': {
                'id': spot.id,
                'name': spot.name,
            },
            'time_from': to_client_timezone(booking.time_from),
            'time_until': to_client_timezone(booking.time_until),
            'status': booking.status,
            'options': booking.options,
        }

    async def _check_permission(self, booking_id: UUID, user_id: UUID) -> Booking:
        if not self.user_repo:
            booking = await self.booking_repo.get_by_id(booking_id)
            if booking.user_id != user_id:
                raise BookingAccessDeniedError
            return booking

        user = await self.user_repo.get_by_id(user_id)
        booking = await self.booking_repo.get_by_id(booking_id)

        if user.is_business:
            return booking

        if booking.user_id != user_id:
            raise BookingAccessDeniedError

        return booking

    async def cancel_booking_with_permission_check(self, booking_id: UUID, user_id: UUID) -> Booking:
        await self._check_permission(booking_id, user_id)
        return await self.cancel_booking(booking_id, user_id)

    async def reschedule_booking(
        self,
        booking_id: UUID,
        user_id: UUID,
        time_from: datetime,
        time_until: datetime,
    ) -> Booking:
        async with self.transaction_manager:
            booking = await self._check_permission(booking_id, user_id)

            active_bookings = await self.booking_repo.get_active_bookings_in_time_range(
                booking.spot_id,
                time_from,
                time_until,
            )

            conflicts = [b for b in active_bookings if b.id != booking_id]

            if conflicts:
                raise BookingOverlapError

            booking.time_from = time_from
            booking.time_until = time_until

            return await self.booking_repo.update(booking)

    async def get_current_booking_for_spot(self, spot_id: UUID, user_id: UUID) -> dict[str, Any]:
        if not self.user_repo:
            raise SpotHasNoCurrentBookingError('User repository is not available')

        user = await self.user_repo.get_by_id(user_id)
        if not user.is_business:
            raise BookingAccessDeniedError

        spot = await self.spot_repo.get_by_id(spot_id)

        now = datetime.now(UTC)

        bookings = await self.booking_repo.get_by_spot_id(spot_id)

        active_bookings: list[Booking] = []
        for booking in bookings:
            booking.status = booking.get_effective_status(now)
            if booking.status == 'active' and booking.time_from <= now <= booking.time_until:
                active_bookings.append(booking)

        if not active_bookings:
            raise SpotHasNoCurrentBookingError(f'No current booking found for spot with ID: {spot_id}')

        booking = active_bookings[0]
        booking_user = await self.user_repo.get_by_id(booking.user_id)

        return {
            'id': booking.id,
            'user': {
                'id': booking_user.id,
                'avatar_url': booking_user.avatar_url,
                'full_name': booking_user.full_name,
                'email': booking_user.email,
            },
            'spot': {
                'id': spot.id,
                'name': spot.name,
            },
            'time_from': to_client_timezone(booking.time_from),
            'time_until': to_client_timezone(booking.time_until),
            'status': booking.status,
            'options': [],
        }

    async def get_all_bookings_paginated(
        self,
        user_id: UUID,
        pagination: Pagination,
    ) -> tuple[list[dict[str, Any]], int]:
        if not self.user_repo:
            return [], 0

        user = await self.user_repo.get_by_id(user_id)
        if not user.is_business:
            raise BookingAccessDeniedError

        total_count = await self.booking_repo.count_all()

        bookings = await self.booking_repo.get_all_paginated(pagination)

        current_time = datetime.now(UTC)
        for booking in bookings:
            booking.status = booking.get_effective_status(current_time)

        result: list[dict[str, Any]] = []
        for booking in bookings:
            booking_user = await self.user_repo.get_by_id(booking.user_id)

            spot = await self.spot_repo.get_by_id(booking.spot_id)

            booking_info: dict[str, Any] = {
                'id': booking.id,
                'user': {
                    'id': booking_user.id,
                    'avatar_url': booking_user.avatar_url,
                    'full_name': booking_user.full_name,
                    'email': booking_user.email,
                },
                'spot': {
                    'id': spot.id,
                    'name': spot.name,
                },
                'time_from': to_client_timezone(booking.time_from),
                'time_until': to_client_timezone(booking.time_until),
                'status': booking.status,
                'options': [],
            }

            result.append(booking_info)

        return result, total_count

    async def suggest_alternative_spot(
        self,
        coworking_id: UUID,
        time_from: datetime,
        time_until: datetime,
        excluded_spot_id: Optional[UUID] = None,
    ) -> Optional[Spot]:
        spots = await self.spot_repo.get_by_coworking_id(coworking_id)

        if not spots:
            return None

        spot_ids = [spot.id for spot in spots if spot.id != excluded_spot_id]

        if not spot_ids:
            return None

        booked_spots = await self.booking_repo.get_active_bookings_for_spots(
            spot_ids,
            time_from,
            time_until,
        )

        booked_spot_ids = {booking.spot_id for booking in booked_spots}

        for spot in spots:
            if spot.id != excluded_spot_id and spot.id not in booked_spot_ids:
                return spot

        return None

    async def get_spot_info(self, spot_id: UUID) -> Spot:
        return await self.spot_repo.get_by_id(spot_id)

    async def add_option_to_booking(self, booking_id: UUID, option_id: UUID, user_id: UUID) -> Booking:
        async with self.transaction_manager:
            booking = await self._check_permission(booking_id, user_id)

            if not self.option_repo:
                msg = 'Option repository is not available'
                raise ValueError(msg)

            try:
                option = await self.option_repo.get_by_id(option_id)

            except Exception as error:
                raise OptionNotFoundError from error

            spot = await self.spot_repo.get_by_id(booking.spot_id)

            if option.coworking_id != spot.coworking_id:
                msg = 'Option does not belong to the same coworking as the booking spot'
                raise ValueError(msg)

            if option_id not in booking.options:
                booking.options.append(option_id)

                return await self.booking_repo.update(booking)

            return booking

    async def get_available_time_slots(self, booking_id: UUID, user_id: UUID) -> list[TimeSlot]:
        booking = await self._check_permission(booking_id, user_id)

        spot = await self.spot_repo.get_by_id(booking.spot_id)

        coworking = await self.coworking_repo.get_by_id(spot.coworking_id)

        booking_date = booking.time_from.date()

        day_start = datetime.combine(booking_date, time.min, tzinfo=booking.time_from.tzinfo)
        day_end = datetime.combine(booking_date, time.max, tzinfo=booking.time_from.tzinfo)

        bookings = await self.booking_repo.get_active_bookings_in_time_range(
            spot_id=spot.id,
            time_from=day_start,
            time_until=day_end,
        )

        bookings = [b for b in bookings if b.id != booking_id]

        bookings.sort(key=lambda b: b.time_from)

        available_slots: list[TimeSlot] = []

        opening_time = datetime.combine(booking_date, coworking.opens_at, tzinfo=booking.time_from.tzinfo)
        closing_time = datetime.combine(booking_date, coworking.closes_at, tzinfo=booking.time_from.tzinfo)

        current_time = opening_time

        for b in bookings:
            if current_time < b.time_from:
                available_slots.append(
                    {
                        'time_from': to_client_timezone(current_time),
                        'time_until': to_client_timezone(b.time_from),
                    },
                )

            current_time = max(current_time, b.time_until)

        if current_time < closing_time:
            available_slots.append(
                {
                    'time_from': to_client_timezone(current_time),
                    'time_until': to_client_timezone(closing_time),
                },
            )

        return available_slots

    async def get_available_time_slots_for_date(self, spot_id: UUID, date: datetime) -> list[TimeSlot]:
        date_utc = to_utc(date)

        spot = await self.spot_repo.get_by_id(spot_id)
        coworking = await self.coworking_repo.get_by_id(spot.coworking_id)

        client_date = to_client_timezone(date_utc).date()

        day_start_client = datetime.combine(client_date, time.min, tzinfo=timezone(DEFAULT_TIMEZONE_OFFSET))
        day_end_client = datetime.combine(client_date, time.max, tzinfo=timezone(DEFAULT_TIMEZONE_OFFSET))

        day_start_utc = to_utc(day_start_client)
        day_end_utc = to_utc(day_end_client)

        bookings = await self.booking_repo.get_active_bookings_in_time_range(
            spot_id=spot_id,
            time_from=day_start_utc,
            time_until=day_end_utc,
        )

        bookings.sort(key=lambda b: b.time_from)

        available_slots: list[TimeSlot] = []

        opening_time_client = datetime.combine(client_date, coworking.opens_at, tzinfo=UTC)
        closing_time_client = datetime.combine(client_date, coworking.closes_at, tzinfo=UTC)

        opening_time = to_client_timezone(opening_time_client)
        closing_time = to_client_timezone(closing_time_client)

        current_time = opening_time

        for b in bookings:
            booking_start = to_client_timezone(b.time_from)
            booking_end = to_client_timezone(b.time_until)

            if current_time < booking_start:
                available_slots.append(
                    {
                        'time_from': current_time,
                        'time_until': booking_start,
                    },
                )

            current_time = max(current_time, booking_end)

        if current_time < closing_time:
            available_slots.append(
                {
                    'time_from': current_time,
                    'time_until': closing_time,
                },
            )

        return available_slots

    def calculate_effective_status(self, bookings: list[Booking]) -> list[Booking]:
        current_time = datetime.now(UTC)

        for booking in bookings:
            booking.status = booking.get_effective_status(current_time)

        return bookings
