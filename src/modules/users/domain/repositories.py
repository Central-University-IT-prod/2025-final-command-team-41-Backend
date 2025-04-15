from src.modules.base.domain.repositories import BaseRepository
from src.modules.users.domain.entities import User


class UserRepository(BaseRepository[User]):
    async def get_by_email(self, email: str) -> User: ...
