from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide  # type: ignore
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.core.database import (
    AsyncSessionProtocol,
    TransactionManager,
    create_async_session_maker,
    create_engine,
)
from src.core.events import EventBus, create_event_bus
from src.core.settings import Settings, get_settings
from src.modules.auth.domain.services import (
    PasswordHasher,
)
from src.modules.auth.infrastructure.services.password_service import (
    ArgonPasswordHasher,
)
from src.modules.storage.application.services import StorageService
from src.modules.storage.domain.repositories import StorageRepository
from src.modules.storage.infrastructure.s3.repository import S3StorageRepository


class EventBusProvider(Provider):
    @provide(scope=Scope.APP)
    def get_event_bus(self, settings: Settings) -> EventBus:
        return create_event_bus(settings)


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def get_engine(self, settings: Settings) -> AsyncEngine:
        return create_engine(settings)

    @provide(scope=Scope.APP)
    def get_session_maker(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return create_async_session_maker(engine)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self,
        session_maker: async_sessionmaker[AsyncSession],
    ) -> AsyncGenerator[AsyncSessionProtocol, None]:
        async with session_maker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def get_transaction_manager(
        self,
        session: AsyncSessionProtocol,
    ) -> TransactionManager:
        return TransactionManager(session)


class PasswordHasherProvider(Provider):
    @provide(scope=Scope.APP)
    def get_password_hasher(self) -> PasswordHasher:
        return ArgonPasswordHasher()


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_dependency(self) -> Settings:
        return get_settings()


class S3StorageProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_storage_repository(self, settings: Settings) -> StorageRepository:
        return S3StorageRepository(
            settings.s3.access_key_id,
            settings.s3.access_key,
            settings.s3.bucket,
        )

    @provide(scope=Scope.REQUEST)
    def get_storage_service(self, storage_repository: StorageRepository) -> StorageService:
        return StorageService(storage_repository)
