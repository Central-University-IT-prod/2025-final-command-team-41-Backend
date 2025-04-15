from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class BookingCreated:
    booking_id: UUID
    user_id: UUID
    spot_id: UUID
    time_from: datetime
    time_until: datetime
    timestamp: datetime


@dataclass(frozen=True)
class BookingCancelled:
    booking_id: UUID
    user_id: UUID
    spot_id: UUID
    time_from: datetime
    time_until: datetime
    timestamp: datetime
