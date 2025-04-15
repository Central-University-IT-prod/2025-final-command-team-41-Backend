from typing import Any

from src.core.logging import get_logger, log_extra
from src.modules.bookings.domain.events import BookingCancelled, BookingCreated

logger = get_logger(__name__)


class BookingEventLogger:
    async def handle(self, event: Any) -> None:
        if isinstance(event, BookingCreated):
            logger.info(
                'Booking created successfully',
                **log_extra(
                    booking_id=event.booking_id,
                    user_id=event.user_id,
                    spot_id=event.spot_id,
                    time_from=event.time_from.isoformat(),
                    time_until=event.time_until.isoformat(),
                    timestamp=event.timestamp.isoformat(),
                ),
            )
        elif isinstance(event, BookingCancelled):
            logger.info(
                'Booking cancelled',
                **log_extra(
                    booking_id=event.booking_id,
                    user_id=event.user_id,
                    spot_id=event.spot_id,
                    time_from=event.time_from.isoformat(),
                    time_until=event.time_until.isoformat(),
                    timestamp=event.timestamp.isoformat(),
                ),
            )
