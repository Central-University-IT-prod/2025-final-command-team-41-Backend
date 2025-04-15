from dishka import AsyncContainer

from src.modules.notifications.application.services import NotificationsService


class NotificationsServiceFactory:
    def __init__(self, container: AsyncContainer) -> None:
        self.container = container

    async def get(self) -> NotificationsService:
        async with self.container() as request_container:
            return await request_container.get(NotificationsService)
