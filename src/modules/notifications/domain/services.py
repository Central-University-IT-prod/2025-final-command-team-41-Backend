from typing import Optional, Protocol
from uuid import UUID

from src.modules.notifications.domain.entities import NotificationType


class FcmNotificationService(Protocol):
    async def send_notification(
        self,
        user_id: UUID,
        notification_type: NotificationType,
        title: str,
        body: str,
        data: Optional[dict[str, str]] = None,
    ) -> bool: ...

    async def send_notification_to_multiple_users(
        self,
        user_ids: list[UUID],
        notification_type: NotificationType,
        title: str,
        body: str,
        data: Optional[dict[str, str]] = None,
    ) -> dict[UUID, bool]: ...
