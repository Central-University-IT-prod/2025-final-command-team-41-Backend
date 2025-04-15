from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.modules.notifications.domain.entities import NotificationType


@dataclass(frozen=True)
class NotificationSent:
    notification_id: UUID
    user_id: UUID
    type: NotificationType
    timestamp: datetime


@dataclass(frozen=True)
class NotificationRead:
    notification_id: UUID
    user_id: UUID
    timestamp: datetime


@dataclass(frozen=True)
class DeviceTokenRegistered:
    token_id: UUID
    user_id: UUID
    token: str
    device_type: str
    timestamp: datetime


@dataclass(frozen=True)
class DeviceTokenRemoved:
    token_id: UUID
    user_id: UUID
    token: str
    timestamp: datetime
