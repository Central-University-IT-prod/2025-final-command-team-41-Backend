from sqlalchemy import select

from src.core.exceptions import NotFoundError
from src.modules.base.infrastructure.repositories.base_repository import BaseRepositoryImpl
from src.modules.users.domain.entities import User
from src.modules.users.domain.repositories import UserRepository
from src.modules.users.infrastructure.orm.models import UserModel


class UserRepositoryImpl(BaseRepositoryImpl[User, UserModel], UserRepository):
    model_type = UserModel

    def _map_to_domain(self, obj: UserModel) -> User:
        return User(
            id=obj.id,
            email=obj.email,
            full_name=obj.full_name,
            hashed_password=obj.hashed_password,
            is_business=obj.is_business,
            is_banned=obj.is_banned,
            avatar_url=obj.avatar_url,
        )

    def _map_to_orm(self, obj: User) -> UserModel:
        return UserModel(
            id=obj.id,
            email=obj.email,
            full_name=obj.full_name,
            hashed_password=obj.hashed_password,
            is_business=obj.is_business,
            is_banned=obj.is_banned,
            avatar_url=obj.avatar_url,
        )

    async def get_by_email(self, email: str) -> User:
        stmt = select(self.model_type).where(self.model_type.email == email)
        result = (await self.db.execute(stmt)).scalar_one_or_none()
        if result is None:
            raise NotFoundError
        return self._map_to_domain(result)
