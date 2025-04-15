from dishka import Provider, Scope, provide  # type: ignore

from src.core.database import (
    AsyncSessionProtocol,
    TransactionManager,
)
from src.core.events import EventBus
from src.core.settings import Settings
from src.modules.notifications.application.services import NotificationsService
from src.modules.notifications.domain.repositories import DeviceTokenRepository, NotificationRepository
from src.modules.notifications.domain.services import FcmNotificationService
from src.modules.notifications.infrastructure.repositories.device_token_repository import (
    DeviceTokenRepositoryImpl,
)
from src.modules.notifications.infrastructure.repositories.notification_repository import (
    NotificationRepositoryImpl,
)
from src.modules.notifications.infrastructure.services.fcm_service import FCMNotificationService


class NotificationsProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_device_token_repository(
        self,
        session: AsyncSessionProtocol,
    ) -> DeviceTokenRepository:
        return DeviceTokenRepositoryImpl(session)

    @provide(scope=Scope.REQUEST)
    def get_notification_repository(
        self,
        session: AsyncSessionProtocol,
    ) -> NotificationRepository:
        return NotificationRepositoryImpl(session)

    @provide(scope=Scope.REQUEST)
    def get_fcm_notification_service(
        self,
        settings: Settings,
        device_token_repository: DeviceTokenRepository,
    ) -> FcmNotificationService:
        return FCMNotificationService(settings, device_token_repository)

    @provide(scope=Scope.REQUEST)
    def get_notification_service(
        self,
        device_token_repo: DeviceTokenRepository,
        notification_repo: NotificationRepository,
        fcm_notification_service: FcmNotificationService,
        event_bus: EventBus,
        transaction_manager: TransactionManager,
    ) -> NotificationsService:
        return NotificationsService(
            device_token_repo,
            notification_repo,
            fcm_notification_service,
            event_bus,
            transaction_manager,
        )
