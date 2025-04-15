from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Optional
from uuid import UUID, uuid4

from src.core.events import EventBus
from src.core.exceptions import NotFoundError
from src.modules.notifications.domain.entities import (
    DeviceToken,
    Notification,
    NotificationType,
)
from src.modules.notifications.domain.events import (
    DeviceTokenRegistered,
    DeviceTokenRemoved,
    NotificationSent,
)
from src.modules.notifications.domain.repositories import (
    DeviceTokenRepository,
    NotificationRepository,
)
from src.modules.notifications.domain.services import FcmNotificationService


@dataclass
class RegisterDeviceTokenCommand:
    repo: DeviceTokenRepository
    user_id: UUID
    token: str
    device_type: str
    event_bus: EventBus

    async def __call__(self) -> DeviceToken:
        try:
            existing_token = await self.repo.get_by_token(self.token)
        except NotFoundError:
            existing_token = None

        if existing_token:
            if existing_token.user_id != self.user_id:
                await self.repo.delete(existing_token.id)
                device_token = DeviceToken(
                    id=uuid4(),
                    user_id=self.user_id,
                    token=self.token,
                    device_type=self.device_type,
                    created_at=datetime.now(UTC),
                )
                await self.repo.create(device_token)
            else:
                device_token = existing_token
                device_token.updated_at = datetime.now(UTC)
                await self.repo.update(device_token)
        else:
            device_token = DeviceToken(
                id=uuid4(),
                user_id=self.user_id,
                token=self.token,
                device_type=self.device_type,
                created_at=datetime.now(UTC),
            )
            await self.repo.create(device_token)

        await self.event_bus.publish(
            DeviceTokenRegistered(
                token_id=device_token.id,
                user_id=self.user_id,
                token=self.token,
                device_type=self.device_type,
                timestamp=datetime.now(UTC),
            ),
        )

        return device_token


@dataclass
class RemoveDeviceTokenCommand:
    repo: DeviceTokenRepository
    token: str
    event_bus: EventBus

    async def __call__(self) -> None:
        try:
            device_token = await self.repo.get_by_token(self.token)
            token_id = device_token.id
            user_id = device_token.user_id
            await self.repo.delete_by_token(self.token)

            await self.event_bus.publish(
                DeviceTokenRemoved(
                    token_id=token_id,
                    user_id=user_id,
                    token=self.token,
                    timestamp=datetime.now(UTC),
                ),
            )
        except NotFoundError:
            return


@dataclass
class SendNotificationCommand:
    notification_repo: NotificationRepository
    notification_service: FcmNotificationService
    user_id: UUID
    type: NotificationType
    title: str
    body: str
    data: Optional[dict[str, str]]
    event_bus: EventBus

    async def __call__(self) -> bool:
        notification = Notification(
            id=uuid4(),
            user_id=self.user_id,
            type=self.type,
            title=self.title,
            body=self.body,
            data=self.data or {},
            created_at=datetime.now(UTC),
        )

        await self.notification_repo.create(notification)

        success = await self.notification_service.send_notification(
            user_id=self.user_id,
            notification_type=self.type,
            title=self.title,
            body=self.body,
            data=self.data,
        )

        await self.event_bus.publish(
            NotificationSent(
                notification_id=notification.id,
                user_id=self.user_id,
                type=self.type,
                timestamp=datetime.now(UTC),
            ),
        )

        return success
