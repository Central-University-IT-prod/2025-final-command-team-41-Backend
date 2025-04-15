from uuid import UUID

from src.core.database import TransactionManager
from src.modules.base.domain.value_objects import Pagination
from src.modules.options.application.commands import CreateOptionCommand, DeleteOptionCommand
from src.modules.options.application.queries import GetOptionsByCoworkingIdQuery, ListOptionsQuery
from src.modules.options.domain.entities import Option
from src.modules.options.domain.repositories import OptionRepository
from src.modules.users.domain.repositories import UserRepository


class OptionService:
    def __init__(
        self,
        repo: OptionRepository,
        user_repo: UserRepository,
        transaction_manager: TransactionManager,
    ) -> None:
        self.repo = repo
        self.user_repo = user_repo
        self.transaction_manager = transaction_manager

    async def create_option(
        self,
        coworking_id: UUID,
        name: str,
        user_id: UUID,
    ) -> Option:
        async with self.transaction_manager:
            command = CreateOptionCommand(
                repo=self.repo,
                user_repo=self.user_repo,
                coworking_id=coworking_id,
                name=name,
                user_id=user_id,
            )
            return await command()

    async def delete_option(self, option_id: UUID, user_id: UUID) -> None:
        async with self.transaction_manager:
            command = DeleteOptionCommand(
                repo=self.repo,
                user_repo=self.user_repo,
                option_id=option_id,
                user_id=user_id,
            )
            await command()

    async def list_options(self, pagination: Pagination) -> list[Option]:
        query = ListOptionsQuery(repo=self.repo)
        return await query(pagination)

    async def get_options_by_coworking(self, coworking_id: UUID) -> list[Option]:
        query = GetOptionsByCoworkingIdQuery(repo=self.repo)
        return await query(coworking_id)
