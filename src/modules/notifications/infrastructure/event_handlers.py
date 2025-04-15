from typing import Any

from src.core.factories import (
    NotificationsServiceFactory,
)
from src.core.logging import get_logger

logger = get_logger(__name__)


class FriendRequestNotificationHandler:
    def __init__(self, service_factory: NotificationsServiceFactory) -> None:
        self.service_factory = service_factory

    async def handle(self, event: Any) -> None:  # noqa
        await self.service_factory.get()
