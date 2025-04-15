from typing import Optional
from uuid import UUID

from src.core.database import TransactionManager
from src.core.events import EventBus
from src.modules.base.domain.value_objects import Pagination
from src.modules.notifications.application.commands import (
    RegisterDeviceTokenCommand,
    RemoveDeviceTokenCommand,
    SendNotificationCommand,
)
from src.modules.notifications.application.queries import (
    GetDeviceTokenByIdQuery,
    GetDeviceTokensQuery,
    GetNotificationByIdQuery,
    GetNotificationsQuery,
)
from src.modules.notifications.domain.entities import (
    DeviceToken,
    Notification,
    NotificationType,
)
from src.modules.notifications.domain.repositories import (
    DeviceTokenRepository,
    NotificationRepository,
)
from src.modules.notifications.domain.services import FcmNotificationService


class NotificationsService:
    def __init__(
        self,
        device_token_repo: DeviceTokenRepository,
        notification_repo: NotificationRepository,
        fcm_notification_service: FcmNotificationService,
        event_bus: EventBus,
        transaction_manager: TransactionManager,
    ) -> None:
        self.device_token_repo = device_token_repo
        self.notification_repo = notification_repo
        self.fcm_notification_service = fcm_notification_service
        self.event_bus = event_bus
        self.transaction_manager = transaction_manager

    async def register_device_token(
        self,
        user_id: UUID,
        token: str,
        device_type: str,
    ) -> DeviceToken:
        async with self.transaction_manager:
            command = RegisterDeviceTokenCommand(
                repo=self.device_token_repo,
                user_id=user_id,
                token=token,
                device_type=device_type,
                event_bus=self.event_bus,
            )
            return await command()

    async def remove_device_token(self, token: str) -> None:
        async with self.transaction_manager:
            command = RemoveDeviceTokenCommand(
                repo=self.device_token_repo,
                token=token,
                event_bus=self.event_bus,
            )
            await command()

    async def get_device_tokens(self, user_id: UUID) -> list[DeviceToken]:
        query = GetDeviceTokensQuery(repo=self.device_token_repo)
        return await query(user_id)

    async def get_device_token(self, token_id: UUID) -> DeviceToken:
        query = GetDeviceTokenByIdQuery(repo=self.device_token_repo)
        return await query(token_id)

    async def send_notification(
        self,
        user_id: UUID,
        notification_type: NotificationType,
        title: str,
        body: str,
        data: Optional[dict[str, str]] = None,
    ) -> bool:
        async with self.transaction_manager:
            command = SendNotificationCommand(
                notification_repo=self.notification_repo,
                notification_service=self.fcm_notification_service,
                user_id=user_id,
                type=notification_type,
                title=title,
                body=body,
                data=data,
                event_bus=self.event_bus,
            )
            return await command()

    async def get_notifications(
        self,
        user_id: UUID,
        pagination: Pagination,
    ) -> list[Notification]:
        query = GetNotificationsQuery(repo=self.notification_repo)
        return await query(user_id, pagination)

    async def get_notification(self, notification_id: UUID) -> Notification:
        query = GetNotificationByIdQuery(repo=self.notification_repo)
        return await query(notification_id)

    async def mark_notification_as_read(self, notification_id: UUID) -> None:
        await self.notification_repo.mark_as_read(notification_id)

    async def mark_all_notifications_as_read(self, user_id: UUID) -> None:
        await self.notification_repo.mark_all_as_read_by_user_id(user_id)
