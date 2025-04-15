from src.core.exceptions import NotFoundError
from src.modules.users.domain.exceptions import UserAlreadyExistsError
from src.modules.users.domain.repositories import UserRepository


class UserValidator:
    @staticmethod
    async def check_email_unique(email: str, repo: UserRepository) -> None:
        try:
            await repo.get_by_email(email)
        except NotFoundError:
            return
        raise UserAlreadyExistsError
