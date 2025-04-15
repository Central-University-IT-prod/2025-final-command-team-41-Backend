from uuid import UUID

from src.modules.base.domain.repositories import BaseRepository
from src.modules.base.domain.value_objects import Pagination
from src.modules.notifications.domain.entities import DeviceToken, Notification


class DeviceTokenRepository(BaseRepository[DeviceToken]):
    async def get_by_user_id(self, user_id: UUID) -> list[DeviceToken]: ...

    async def get_by_token(self, token: str) -> DeviceToken: ...

    async def delete_by_token(self, token: str) -> None: ...


class NotificationRepository(BaseRepository[Notification]):
    async def get_paginated_by_user_id(
        self,
        user_id: UUID,
        pagination: Pagination,
    ) -> list[Notification]: ...

    async def mark_as_read(self, notification_id: UUID) -> None: ...

    async def mark_all_as_read_by_user_id(self, user_id: UUID) -> None: ...

    async def delete_all_by_user_id(self, user_id: UUID) -> None: ...
