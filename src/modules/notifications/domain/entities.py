from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from uuid import UUID

from src.core.domain import BaseDomain


class NotificationType(Enum):
    FRIEND_REQUEST = auto()
    FRIEND_REQUEST_ACCEPTED = auto()
    FRIEND_REQUEST_REJECTED = auto()
    FRIEND_REQUEST_DELETED = auto()
    FRIENDSHIP_REMOVED = auto()
    SYSTEM = auto()


@dataclass
class DeviceToken(BaseDomain):
    user_id: UUID
    token: str
    device_type: str
    created_at: datetime
    updated_at: datetime | None = None


@dataclass
class Notification(BaseDomain):
    user_id: UUID
    type: NotificationType
    title: str
    body: str
    data: dict[str, str]
    created_at: datetime
    read_at: datetime | None = None
