from dishka import Provider, Scope, provide  # type: ignore

from src.core.database import (
    AsyncSessionProtocol,
    TransactionManager,
)
from src.core.events import EventBus
from src.modules.auth.domain.services import (
    PasswordHasher,
)
from src.modules.storage.application.services import StorageService
from src.modules.users.application.services import UserService
from src.modules.users.domain.repositories import UserRepository
from src.modules.users.infrastructure.repositories.user_repository import (
    UserRepositoryImpl,
)


class UserProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_user_repository(self, session: AsyncSessionProtocol) -> UserRepository:
        return UserRepositoryImpl(session)

    @provide(scope=Scope.REQUEST)
    def get_user_service(
        self,
        repo: UserRepository,
        password_hasher: PasswordHasher,
        event_bus: EventBus,
        transaction_manager: TransactionManager,
        storage_service: StorageService,
    ) -> UserService:
        return UserService(repo, password_hasher, event_bus, transaction_manager, storage_service)
