from dishka import Provider, Scope, provide

from src.core.database import AsyncSessionProtocol, TransactionManager
from src.modules.coworkings.application.services import CoworkingService
from src.modules.coworkings.domain.repositories import CoworkingRepository
from src.modules.coworkings.infrastructure.repositories.coworking_repository import CoworkingRepositoryImpl
from src.modules.storage.application.services import StorageService


class CoworkingProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_coworkings_repository(
        self,
        session: AsyncSessionProtocol,
    ) -> CoworkingRepository:
        return CoworkingRepositoryImpl(session)

    @provide(scope=Scope.REQUEST)
    def get_coworking_service(
        self,
        repo: CoworkingRepository,
        transaction_manager: TransactionManager,
        storage_service: StorageService,
    ) -> CoworkingService:
        return CoworkingService(repo, transaction_manager, storage_service)
