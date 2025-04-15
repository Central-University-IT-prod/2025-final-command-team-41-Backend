from dataclasses import dataclass
from uuid import UUID

from src.modules.base.domain.value_objects import Pagination
from src.modules.notifications.domain.entities import DeviceToken, Notification
from src.modules.notifications.domain.repositories import (
    DeviceTokenRepository,
    NotificationRepository,
)


@dataclass
class GetDeviceTokensQuery:
    repo: DeviceTokenRepository

    async def __call__(self, user_id: UUID) -> list[DeviceToken]:
        return await self.repo.get_by_user_id(user_id)


@dataclass
class GetDeviceTokenByIdQuery:
    repo: DeviceTokenRepository

    async def __call__(self, token_id: UUID) -> DeviceToken:
        return await self.repo.get_by_id(token_id)


@dataclass
class GetNotificationsQuery:
    repo: NotificationRepository

    async def __call__(self, user_id: UUID, pagination: Pagination) -> list[Notification]:
        return await self.repo.get_paginated_by_user_id(user_id, pagination)


@dataclass
class GetNotificationByIdQuery:
    repo: NotificationRepository

    async def __call__(self, notification_id: UUID) -> Notification:
        return await self.repo.get_by_id(notification_id)
