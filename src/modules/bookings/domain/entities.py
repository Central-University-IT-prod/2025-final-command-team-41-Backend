import datetime
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from src.core.domain import BaseDomain


@dataclass
class Booking(BaseDomain):
    user_id: UUID
    spot_id: UUID
    time_from: datetime.datetime
    time_until: datetime.datetime
    status: str = 'active'  # active, cancelled, expired
    options: list[UUID] = field(default_factory=list)

    def get_effective_status(self, current_time: Optional[datetime.datetime] = None) -> str:
        if current_time is None:
            current_time = datetime.datetime.now(datetime.UTC)

        if self.status == 'cancelled':
            return 'cancelled'

        if current_time > self.time_until:
            return 'expired'

        return 'active'
