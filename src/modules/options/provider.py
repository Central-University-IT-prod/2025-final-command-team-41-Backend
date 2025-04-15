from dishka import Provider, Scope, provide

from src.core.database import AsyncSessionProtocol, TransactionManager
from src.modules.options.application.services import OptionService
from src.modules.options.domain.repositories import OptionRepository
from src.modules.options.infrastructure.repositories.option_repository import (
    OptionRepositoryImpl,
)
from src.modules.users.domain.repositories import UserRepository


class OptionProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_option_repository(self, session: AsyncSessionProtocol) -> OptionRepository:
        return OptionRepositoryImpl(session)

    @provide(scope=Scope.REQUEST)
    def get_option_service(
        self,
        repo: OptionRepository,
        user_repo: UserRepository,
        transaction_manager: TransactionManager,
    ) -> OptionService:
        return OptionService(repo, user_repo, transaction_manager)
