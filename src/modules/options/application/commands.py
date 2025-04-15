from dataclasses import dataclass
from uuid import UUID, uuid4

from src.modules.options.domain.entities import Option
from src.modules.options.domain.exceptions import NotBusinessUserError
from src.modules.options.domain.repositories import OptionRepository
from src.modules.users.domain.repositories import UserRepository


@dataclass
class CreateOptionCommand:
    repo: OptionRepository
    user_repo: UserRepository
    coworking_id: UUID
    name: str
    user_id: UUID

    async def __call__(self) -> Option:
        user = await self.user_repo.get_by_id(self.user_id)
        if not user.is_business:
            raise NotBusinessUserError

        option = Option(
            id=uuid4(),
            coworking_id=self.coworking_id,
            name=self.name,
        )
        await self.repo.create(option)
        return option


@dataclass
class DeleteOptionCommand:
    repo: OptionRepository
    user_repo: UserRepository
    option_id: UUID
    user_id: UUID

    async def __call__(self) -> None:
        user = await self.user_repo.get_by_id(self.user_id)
        if not user.is_business:
            raise NotBusinessUserError

        await self.repo.delete(self.option_id)
